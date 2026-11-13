# Fallback plan

Rule for the day: **the panel scores how you handle a failure, not whether one happens.** Name the problem in one sentence, switch to the backup, keep the story and the clock. Never debug live for more than 30 seconds.

One sentence that works for every case:

> "Live systems do this. I recorded this exact flow yesterday on the same environment, so let me show you that and keep to time."

## The three backups

| Backup | What it is | When you use it |
|---|---|---|
| **A. Pre-triggered alert** | A real alert that is already in Slack and in Elastic, made 20 minutes before the session. | The live alert does not arrive in time. |
| **B. Screenshots in order** | 10 numbered screenshots in one folder or one PDF. | One screen fails (AI, a page does not load). |
| **C. Screen recording** | One video of the whole 12-minute flow, without sound. You narrate live. | The shop, the network or Elastic Cloud fails. |

All three come from your rehearsal. Make them the evening before, on the real trial environment, after everything works.

## How to record the backups (30 minutes, the evening before)

1. Run `scripts/reset.sh`, then `scripts/preflight.sh`. All green.
2. Set up the browser tabs exactly as in `RUNBOOK.md`. Same zoom, same window size as on the day.
3. **Start recording.** On macOS: press `Shift + Command + 5`, choose "Record Selected Portion", select the browser and terminal area, **Options > Microphone: None**, click **Record**.
4. Walk through the whole runbook at normal speed, without speaking. Pause 2 seconds on every screen you would point at.
5. Stop with the stop button in the menu bar. Save as `recordings/demo-backup.mov`. The `recordings/` folder is in `.gitignore`.
6. Watch it once. Check that no API key, webhook URL or personal data is visible. If something is, record again.
7. **Screenshots.** Play the video and take one screenshot per step (`Shift + Command + 4`). Name them so they sort:

   | File | Shows |
   |---|---|
   | `01-dashboard-healthy.png` | Business dashboard, everything normal |
   | `02-service-map.png` | Service map |
   | `03-slack-alert.png` | The alert message in Slack |
   | `04-alert-details.png` | Alert details page with the chart |
   | `05-ai-investigating.png` | AI Agent after "Add to chat" |
   | `06-ai-root-cause.png` | The AI answer naming product-catalog |
   | `07-trace-waterfall.png` | Trace with the 30-second SQL span |
   | `08-log-line.png` | The lock contention log line |
   | `09-dashboard-impact.png` | Dashboard during the incident, SLO panels |
   | `10-slack-recovered.png` | RECOVERED message in Slack |

8. Put the ten screenshots into one PDF (select them in Finder > right-click > Quick Actions > Create PDF). Keep it open in Preview on the day.
9. Copy the video and the PDF to a second place (phone or USB stick). If the laptop dies you can still present from another machine.

**Pre-triggered alert (backup A), on the day, 20 minutes before:**

```bash
scripts/break.sh
# wait for the Slack alert (1 to 2 minutes), then
scripts/reset.sh
```

Slack now holds a real ALERT and a real RECOVERED message, and Elastic holds a real alert with real traces behind it. Keep that alert's page open in a spare tab. Then run `scripts/preflight.sh --quiet` again.

## What to do when something fails

### Case A. The Slack alert does not arrive (check at 3:00)

1. Open **Observability > Alerts** in Kibana. If the alert is there and "Active", open it and say: "The alert fired in Elastic. Slack is slow to deliver, so I open it from here." Continue at 2:40 in the runbook.
2. If there is no alert in Elastic either, switch to the pre-triggered alert in the spare tab: "I ran the same failure 20 minutes ago as a safety net. This is that alert." Set the time picker to the last hour. Everything after that works the same, on real data.
3. Do not re-run `break.sh`. You do not have the minutes.

### Case B. The shop or the data flow is down

Signs: preflight failed before the session, the dashboard is empty, Docker crashed.

1. If you notice **before** the session and have 5 minutes: `scripts/stop-demo.sh` then `scripts/start-demo.sh`. Data from the earlier run is still in Elastic.
2. If you notice **during** the session: use the pre-triggered alert (case A, step 2). The data in Elastic does not need the shop to be running. Skip the live `break.sh` and `fix.sh`. Say: "The shop on my laptop is not cooperating, but the data from the run 20 minutes ago is all in Elastic. Let me investigate that incident."
3. If Elastic has no usable data at all: play the recording (case D).

### Case C. The AI Agent fails or answers badly

- Slow (more than 45 seconds): keep talking, switch to the trace view (runbook 6:20), come back to the chat later.
- Bad answer: follow "If the AI answers poorly" in `RUNBOOK.md`.
- Error or no model (trial token limit): show screenshots `05` and `06`. Say: "The trial account limits LLM usage and I have hit that limit. This is the answer from yesterday's run on the same incident." Then do the manual path live. The manual path is the proof. Mention that in production the limit does not apply, and that customers can also connect their own model.

### Case D. No network, Elastic Cloud unreachable, or the laptop misbehaves

1. Play `recordings/demo-backup.mov` full screen and **narrate it live** with the runbook talk track. Pause where you would point.
2. If video playback also fails, walk through the PDF of screenshots.
3. Keep the same timing checkpoints. A narrated recording that ends on time is a good demo.

Optional, only with 10 spare minutes before the session and a working laptop: start the local stack (`SETUP.md` step 11). It works offline but has no AI Agent answers.

### Case E. Screen sharing shows the wrong window or is unreadable

Stop sharing, share the **entire screen** instead of a window, zoom the browser to 150%. Ask: "Can everyone read the numbers on the tiles?" That takes 15 seconds and shows care for the audience.

### Case F. You are running over

Cut in this order: optional prompt 4, the German summary (prompt 3), the log line step (7:20), the shop tab (0:20). Never cut: the Slack alert, the AI root cause, the business dashboard, the recap.

## The 3 biggest risks and how they are covered

| Risk | Likelihood | Cover |
|---|---|---|
| 1. The AI Agent answers slowly, vaguely or not at all (trial token limit, model variance). Untested in this kit. | Medium | Tested manual path through traces and logs (runbook 6:20). Narrow prompts. Screenshots 05 and 06. |
| 2. The live alert is late or missing (laptop under load, Docker, network to Elastic Cloud, Slack delivery). | Medium | Hard check at 3:00. Open the alert in Elastic directly. Pre-triggered alert from 20 minutes before. |
| 3. Environment loss: trial expired or suspended, Elastic Cloud or Wi-Fi unreachable, shop will not start. | Low, but total | Trial start date with margin. Preflight 30 and 5 minutes before. Recording and screenshot PDF on a second device. Local stack as last resort. |
