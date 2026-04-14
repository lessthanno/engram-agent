# I Built the Tool That Atomic Habits Assumed You'd Do Manually

I've read Atomic Habits three times.

Each time I think "yes, exactly." Two weeks later I'm back to the old patterns.

James Clear says: track your habits. That's the foundation. He includes a tracking sheet.

I lasted 4 days.

Not laziness. The problem: manual tracking is itself a habit, and building a "habit of tracking habits" while trying to build other habits stacks two hard things. The failure mode is designed in.

---

## So I automated it

I built a tool that observes my behavior without me doing anything:
- Which repos I committed to, and when
- How many projects I switched between each day
- Which tasks I started but never finished
- What my high-output days looked like vs low-output days

It runs automatically every week. Claude synthesizes the data into a report. No dashboard, no app, no account. Just a file on my machine.

Here's what last week's report actually said.

---

## This week's real data

```
Focus Score: 6/10

329 commits across 12 repos this week.
High output, but chronic fragmentation — you never fully left any codebase.

Pattern detected:
Apr 13 produced 202 commits — 9.2x the weekly daily average of 22.
The prior 4 days averaged 8 commits/day.
Something unlocked on Apr 12 (68 commits) that carried into Apr 13.
This isn't random variance. It's a mode switch.
When you hit that mode, throughput multiplied by 9x.

Time reality:
5 out of 7 days operated at sub-10% of your demonstrated capacity.
The ceiling exists. The floor is the problem.
```

I read that three times.

Not because the numbers are impressive. Because **I don't know what happened on Apr 13.**

What did I do differently that day? No meetings? Stayed in one repo? Something in my environment? I have no idea. That's exactly the problem.

---

## This is what Clear is actually talking about

Law 1: **Make it Obvious.**

You can't change what you can't see.

Before this report, I thought my output was decent. "Shipped some code today, good." But the data says: you have 9x capacity. On 5 out of 7 days, you used less than 10% of it.

Manual tracking never finds this. You can't proactively track patterns you don't know exist. Automatic observation can.

---

## Three other things the tool found

**12 repos active, most unfinished**

`news`, `uyux`, `x-agent-waitlist` all had activity this week — but only a few touches each. Started, abandoned. The tool estimated 8–10 open unresolved threads.

I thought I was running parallel projects. The data says I'm running a loop of starting and shelving.

**The advice wasn't generic**

It didn't say "improve focus" or "reduce context switching." It said:

> "Figure out what was different on Apr 13 and protect that condition. The trigger is in your environment or schedule. Find the variable, engineer it to repeat. Everything else is secondary."

That came from my data. Not from a productivity book.

---

## The Atomic Habits connection

Clear's third law: **Make it Easy.**

Manual tracking fails because the system has friction. You have to remember to open the app, log something, maintain a streak. One missed day and the streak breaks.

Removing logging entirely removes that failure mode. The system runs whether I open it or not. There's nothing to forget.

This is the part Clear describes but assumes you have to do yourself. You don't.

---

## It's called Mirror

Zero manual input. You work normally. AI watches. Every Sunday night, you see who you actually are — not who you think you are.

100% local. No cloud, no accounts, no telemetry. Open source, free.

```bash
git clone https://github.com/lessthanno/engram-agent.git ~/engram-agent
bash ~/engram-agent/scripts/install.sh

# Run now
python3 ~/engram-agent/core/mirror.py
```

Works with Claude Code (free, if you have it) or any Anthropic API key. If neither — it still collects your data and you can add the key later.

Project: **github.com/lessthanno/engram-agent**

---

If you've read Atomic Habits and thought "this makes sense but I can't make it stick" — maybe the problem isn't willpower. Maybe the problem is that tracking itself requires willpower.

Make the tracking zero effort. See what happens.

---

*All numbers in this post are from Mirror's auto-generated report for the week of Apr 7–14, 2026. Real data, anonymized.*
