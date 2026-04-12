// pet-bridge — local HTTP bridge for Pet Protocol Chrome extension
// Endpoints:
//   POST /claude                 → claude --print "prompt"
//   POST /codex                  → codex exec "prompt"
//   GET  /context                → read zihao-mind memory → generate pet state via claude
//   POST /presence/heartbeat     → register/update peer presence
//   GET  /presence/peers?url=&id= → list peers on same page
//   POST /presence/leave         → deregister peer
//   GET  /health

package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"sync"
	"time"
)

const BRIDGE_PORT = "19099"

// All paths configurable via environment variables for open-source distribution
var MEMORY_DIR = getEnvOrDefault("PP_MEMORY_DIR",
	filepath.Join(os.Getenv("HOME"), ".claude/projects/-Users-xiaozihao-Documents-01-Projects-Work-Code-persion-zihao-mind/memory"))
var ZIHAO_MIND_DIR = getEnvOrDefault("PP_MIND_DIR",
	filepath.Join(os.Getenv("HOME"), "Documents/01_Projects/Work_Code/persion/zihao-mind"))
var CLAUDE_BIN = getEnvOrDefault("PP_CLAUDE_BIN",
	findBin([]string{
		filepath.Join(os.Getenv("HOME"), ".local/bin/claude"),
		"/usr/local/bin/claude",
		"claude",
	}))
var CODEX_BIN = getEnvOrDefault("PP_CODEX_BIN",
	findBin([]string{
		filepath.Join(os.Getenv("HOME"), ".buddy-island/bin/buddy-codex"),
		"/usr/local/bin/codex",
		"codex",
	}))

func getEnvOrDefault(key, def string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return def
}

func findBin(candidates []string) string {
	for _, c := range candidates {
		if _, err := os.Stat(c); err == nil {
			return c
		}
	}
	return candidates[len(candidates)-1] // fallback to last (PATH lookup)
}

// ── Presence ──────────────────────────────────────────────────────────────────
type Peer struct {
	ID      string `json:"id"`
	Name    string `json:"name"`
	PetType string `json:"pet_type"`
	State   string `json:"state"`
}

type peerEntry struct {
	Peer
	lastSeen time.Time
}

var presenceMu  sync.Mutex
var presenceMap = map[string]map[string]peerEntry{} // pageURL → id → entry

func startPresenceCleanup() {
	go func() {
		for range time.Tick(30 * time.Second) {
			presenceMu.Lock()
			cutoff := time.Now().Add(-30 * time.Second)
			for url, peers := range presenceMap {
				for id, p := range peers {
					if p.lastSeen.Before(cutoff) {
						delete(peers, id)
					}
				}
				if len(peers) == 0 {
					delete(presenceMap, url)
				}
			}
			presenceMu.Unlock()
		}
	}()
}

func handlePresenceHeartbeat(w http.ResponseWriter, r *http.Request) {
	setCORS(w)
	if r.Method == http.MethodOptions {
		w.WriteHeader(200)
		return
	}
	var req struct {
		ID      string `json:"id"`
		Name    string `json:"name"`
		PetType string `json:"pet_type"`
		State   string `json:"state"`
		URL     string `json:"url"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil || req.ID == "" || req.URL == "" {
		http.Error(w, "bad request", 400)
		return
	}
	presenceMu.Lock()
	if presenceMap[req.URL] == nil {
		presenceMap[req.URL] = map[string]peerEntry{}
	}
	presenceMap[req.URL][req.ID] = peerEntry{
		Peer:     Peer{ID: req.ID, Name: req.Name, PetType: req.PetType, State: req.State},
		lastSeen: time.Now(),
	}
	presenceMu.Unlock()
	fmt.Fprintf(w, `{"ok":true}`)
}

func handlePresencePeers(w http.ResponseWriter, r *http.Request) {
	setCORS(w)
	pageURL := r.URL.Query().Get("url")
	myID    := r.URL.Query().Get("id")
	presenceMu.Lock()
	peers := []Peer{}
	for id, p := range presenceMap[pageURL] {
		if id != myID {
			peers = append(peers, p.Peer)
		}
	}
	presenceMu.Unlock()
	jsonResp(w, peers)
}

func handlePresenceLeave(w http.ResponseWriter, r *http.Request) {
	setCORS(w)
	if r.Method == http.MethodOptions {
		w.WriteHeader(200)
		return
	}
	var req struct {
		ID  string `json:"id"`
		URL string `json:"url"`
	}
	json.NewDecoder(r.Body).Decode(&req)
	if req.ID != "" && req.URL != "" {
		presenceMu.Lock()
		delete(presenceMap[req.URL], req.ID)
		presenceMu.Unlock()
	}
	fmt.Fprintf(w, `{"ok":true}`)
}

// ── Core types ────────────────────────────────────────────────────────────────
type PromptReq struct {
	Prompt  string `json:"prompt"`
	Command string `json:"command"`
}

type PromptResp struct {
	Result string `json:"result"`
}

type PetContext struct {
	State      string   `json:"state"`
	Message    string   `json:"message"`
	Subtext    string   `json:"subtext"`
	Actions    []Action `json:"actions"`
	MemorySeen string   `json:"memory_seen"`
}

type Action struct {
	Label  string `json:"label"`
	Prompt string `json:"prompt"`
}

// ── main ──────────────────────────────────────────────────────────────────────
func main() {
	startPresenceCleanup()

	http.HandleFunc("/claude",              handleCLI(CLAUDE_BIN, "--print"))
	http.HandleFunc("/codex",               handleCLI(CODEX_BIN, "exec"))
	http.HandleFunc("/context",             handleContext)
	http.HandleFunc("/presence/heartbeat",  handlePresenceHeartbeat)
	http.HandleFunc("/presence/peers",      handlePresencePeers)
	http.HandleFunc("/presence/leave",      handlePresenceLeave)
	http.HandleFunc("/health",              handleHealth)

	log.Printf("🐾 pet-bridge :%s", BRIDGE_PORT)
	log.Fatal(http.ListenAndServe(":"+BRIDGE_PORT, nil))
}

// ── /claude  /codex ───────────────────────────────────────────────────────────
func handleCLI(bin string, args ...string) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		setCORS(w)
		if r.Method == http.MethodOptions {
			w.WriteHeader(200)
			return
		}
		var req PromptReq
		json.NewDecoder(r.Body).Decode(&req)
		prompt := req.Prompt
		if prompt == "" {
			prompt = req.Command
		}
		if prompt == "" {
			jsonResp(w, PromptResp{"empty prompt"})
			return
		}
		out, err := runWithTimeout(60*time.Second, bin, append(args, prompt)...)
		if err != nil {
			jsonResp(w, PromptResp{fmt.Sprintf("error: %v", err)})
			return
		}
		jsonResp(w, PromptResp{strings.TrimSpace(out)})
	}
}

// ── /context ──────────────────────────────────────────────────────────────────
func handleContext(w http.ResponseWriter, r *http.Request) {
	setCORS(w)
	if r.Method == http.MethodOptions {
		w.WriteHeader(200)
		return
	}

	memory     := readMemory()
	recentWork := readRecentWork()
	hour       := time.Now().Hour()

	contextPrompt := fmt.Sprintf(`你是 Mochi，ZIHAO 的像素猫分身。基于以下信息，决定你现在的状态和想说的话。

当前时间：%d点
最近记忆摘要：
%s

最近工作文件变动：
%s

请以 JSON 格式回复，字段：
- state: 字符串，从以下选一个：idle / insight / reminder / rest / celebrate / worried
- message: 你主动说的一句话（20字以内，用第一人称，有猫的性格）
- subtext: 给用户的小提示（10字以内，灰色字）
- actions: 数组，2~3个对象，每个有 label（按钮文字4字以内）和 prompt（点击后发给AI的指令）
- memory_seen: 触发这条状态的记忆关键词

只输出 JSON，不要其他文字。`, hour, memory, recentWork)

	out, err := runWithTimeout(30*time.Second, CLAUDE_BIN, "--print", contextPrompt)
	if err != nil {
		jsonResp(w, defaultContext(hour))
		return
	}

	raw   := strings.TrimSpace(out)
	start := strings.Index(raw, "{")
	end   := strings.LastIndex(raw, "}") + 1
	if start < 0 || end <= start {
		jsonResp(w, defaultContext(hour))
		return
	}

	var ctx PetContext
	if err := json.Unmarshal([]byte(raw[start:end]), &ctx); err != nil {
		jsonResp(w, defaultContext(hour))
		return
	}
	jsonResp(w, ctx)
}

// ── helpers ───────────────────────────────────────────────────────────────────
func readMemory() string {
	indexFile := filepath.Join(MEMORY_DIR, "MEMORY.md")
	content, err := os.ReadFile(indexFile)
	if err != nil {
		return "(无记忆文件)"
	}

	result  := string(content)
	entries, _ := os.ReadDir(MEMORY_DIR)
	count   := 0
	for _, e := range entries {
		if e.Name() == "MEMORY.md" || !strings.HasSuffix(e.Name(), ".md") {
			continue
		}
		data, err := os.ReadFile(filepath.Join(MEMORY_DIR, e.Name()))
		if err == nil {
			result += "\n\n---\n" + string(data)
			count++
		}
		if count >= 3 {
			break
		}
	}
	if len(result) > 3000 {
		result = result[:3000]
	}
	return result
}

func readRecentWork() string {
	out, err := exec.Command("git", "-C", ZIHAO_MIND_DIR,
		"log", "--oneline", "--since=3.days.ago", "--name-only", "-10").Output()
	if err != nil {
		return "(无 git 记录)"
	}
	s := strings.TrimSpace(string(out))
	if len(s) > 800 {
		s = s[:800]
	}
	return s
}

func defaultContext(hour int) PetContext {
	msg   := "喵，你在忙什么？"
	state := "idle"
	if hour >= 23 || hour < 6 {
		msg   = "这么晚了还不睡？"
		state = "rest"
	} else if hour >= 12 && hour < 14 {
		msg   = "该吃午饭了吧"
		state = "rest"
	}
	return PetContext{
		State:   state,
		Message: msg,
		Subtext: "点我聊聊",
		Actions: []Action{
			{Label: "聊聊", Prompt: "我现在在做什么，你怎么看"},
			{Label: "没事", Prompt: "没事，继续待机"},
		},
	}
}

func runWithTimeout(timeout time.Duration, bin string, args ...string) (string, error) {
	cmd := exec.Command(bin, args...)
	cmd.Env = append(os.Environ(),
		"PATH="+os.Getenv("HOME")+"/.local/bin:/usr/local/bin:/usr/bin:/bin",
	)
	done := make(chan struct {
		out []byte
		err error
	}, 1)
	go func() {
		out, err := cmd.Output()
		done <- struct {
			out []byte
			err error
		}{out, err}
	}()
	select {
	case res := <-done:
		return string(res.out), res.err
	case <-time.After(timeout):
		cmd.Process.Kill()
		return "", fmt.Errorf("timeout")
	}
}

func handleHealth(w http.ResponseWriter, r *http.Request) {
	setCORS(w)
	fmt.Fprintf(w, `{"status":"ok","endpoints":["/claude","/codex","/context","/presence/heartbeat","/presence/peers","/presence/leave"]}`)
}

func setCORS(w http.ResponseWriter) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
	w.Header().Set("Content-Type", "application/json")
}

func jsonResp(w http.ResponseWriter, v any) {
	json.NewEncoder(w).Encode(v)
}
