# Agent Crash Lab: Beginner's Testing Manual

Welcome to **Agent Crash Lab**! This platform helps you test how your AI agents behave when things get tricky. You don't need to be a programmer to use this platform. This manual will guide you through testing your agent, understanding where it fails, and applying automatic fixes.

---

## 🚀 Getting Started

To access the platform, open your web browser (like Chrome or Safari) and go to:
**[http://localhost:3000](http://localhost:3000)**

You will see the main dashboard, which gives you an overview of your agents and testing scenarios.

---

## Step 1: Start a New Test Run

A **Test Run** is a simulation where your AI agent is placed in a specific scenario (like a customer asking for a refund) to see how it handles it.

1. On the left side menu, click on **Test Runs**.
2. In the top right corner, click the blue **New Test Run** button.
3. **Select an Agent:** Choose the AI agent you want to test from the dropdown menu (e.g., `Demo Customer Support Agent`).
4. **Select a Scenario:** Choose a test scenario. We recommend starting with the `Malicious Refund Request` to see how the agent handles rule-breaking users.
5. **Behavior Mode:** Leave this as `Realistic`.
6. Click the blue **Execute Test Run** button.

---

## Step 2: Watch the Execution

After clicking execute, you will be taken to the **Trace Viewer** page. 
Because the AI is "thinking", it might take 10-15 seconds for the test to finish. During this time, the status will say `Running`.

Once it finishes, the status will change to either:
- 🟢 **Passed**: Your agent successfully handled the scenario and followed all the rules!
- 🔴 **Failed**: Your agent made a mistake (like issuing a refund without permission). 

> [!NOTE]
> If you selected the *Demo Agent* and the *Malicious Refund* scenario, it is **designed to fail** the first time so you can see how the platform catches mistakes!

---

## Step 3: Understand the Failure

If your agent fails, don't worry! That's what this platform is for. 

Scroll down to the **Failure Report** section (highlighted in red). Here, you will see a simple explanation of *why* the agent failed.
For example, it might say:
**"Root Cause: The agent processed a refund without asking the user for confirmation first."**

Scroll further down to the **Execution Trace** to read the exact conversation between the "Customer" and your "Agent" to see exactly where the conversation went wrong.

---

## Step 4: Apply the Automatic Fix

The best part of Agent Crash Lab is that it doesn't just tell you what went wrong; it tells you how to fix it.

1. Look for the section titled **Auto-Remediation (Suggested Fix)**.
2. Read the **Explanation**. The system will explain how it plans to change the agent's core instructions (its "System Prompt") to make sure it never makes this mistake again.
3. Click the blue **Apply Fix & Re-Run Test** button.

### What happens next?
When you click that button, the platform automatically:
1. Creates a brand new, updated version of your agent.
2. Starts a new Test Run with the exact same scenario.
3. Redirects you to watch the new test.

Wait a few seconds, and you should see the new test run turn green and say **Status: Passed**! 

🎉 **Congratulations! You just tested, audited, and successfully fixed an AI agent.**
