# Zhiyuxing Project Report

[中文](project-report.md) | [English](project-report.en.md)

> This document keeps the fuller project background, flowcharts, and interface illustrations. For public-facing project usage, start with [README_EN.md](../README_EN.md).

## 1. Positioning

**Zhiyuxing** is an AI assistant for college student scenarios, focused on emotional support and study enablement. It combines LLM-based conversation, psychology-informed guidance, and possible DingTalk ecosystem integration to provide more timely and personalized support.

Compared with a general-purpose Q&A assistant, this project emphasizes:

- real student scenarios such as academic stress, social anxiety, self-doubt, procrastination, and study-related mental fatigue
- study guidance that adapts to emotional state rather than only recommending generic learning methods
- a deployable campus-oriented usage path, originally envisioned around DingTalk

## 2. Problem Background

Typical sources of stress for college students include:

- long-term academic competition and pressure
- social disconnection and interpersonal anxiety
- uncertainty about future direction and self-worth
- ongoing stress caused by the job market

Traditional counseling resources are often limited in capacity, coverage, and scheduling speed. The project aims to explore whether AI can help fill the gap for high-frequency, small-step, immediate support.

## 3. Core Goals

### 3.1 Emotional Support

- provide an immediate, non-judgmental place to talk
- reduce anxiety and pressure through empathetic dialogue and basic cognitive guidance
- gently encourage offline professional support when higher-risk expressions are detected

### 3.2 Study Enablement

- match study methods and action guidance to emotional and motivational states
- provide strategies for time management, memory techniques, and study rhythm adjustment
- help users move from emotional overload back into executable action

![Project Goals Flow](assets/02-project-goals-flow.png)

*Project goals flowchart*

## 4. Functional Design

### 4.1 Emotional Support Module

1. **Emotion recognition and timely response**  
   Analyze text input, identify signals such as anxiety, stress, and low mood, and generate more empathetic responses.

2. **Safe space for expression**  
   Provide an anonymous, low-friction, non-judgmental channel for support.

3. **Basic psychological guidance**  
   Draw on ideas such as CBT, emotion regulation, and positive psychology to offer supportive guidance.

4. **Risk detection and referral**  
   If higher-risk expressions appear, the system should prioritize warning and referral rather than continuing casual conversation.

### 4.2 Study Guidance Module

1. **Diverse study strategy recommendations**  
   For example: Pomodoro, mind mapping, spaced repetition, and other familiar methods.

2. **Dynamic adaptation**  
   Adjust the guidance style based on stress, procrastination, and attention-related issues.

3. **Intervention for study-related internal friction**  
   First regulate emotion, then break down action steps to rebuild momentum.

4. **Personalized study plan generation**  
   Suggest action paths based on emotional traits, study style, and task goals.

### 4.3 DingTalk Ecosystem Integration

- integrate with DingTalk groups, schedules, and tasks
- support message-triggered workflows and reminders
- use organizational capabilities for permissions, identity, and data protection

![Core Features Flow](assets/03-core-features-flow.png)

*Core features flowchart*

## 5. Innovation Points

### 5.1 Combined Effects

The project treats emotional support and study enablement as one linked system instead of two separate functions. Better emotional state can improve action, and action feedback can improve emotional state in return.

### 5.2 Emotion-Learning Loop

The goal is not only to comfort users, and not only to provide methods, but to create a loop of:

`emotion regulation -> study strategy -> action feedback`

### 5.3 Ethical Design

The concept explicitly emphasizes:

- crisis expression detection and referral
- not treating AI as a replacement for professional medical care
- privacy protection and risk boundaries

![Innovation Workflow](assets/04-innovation-workflow.png)

*Innovation workflow*

![Emotion-Learning Loop](assets/05-heart-learning-loop.png)

*Emotion-learning loop*

## 6. Technical Approach

Based on the original competition-style materials, the technical direction included:

- **LLM capability**: DingTalk-hosted models or compatible model providers, combined with prompt design
- **Knowledge sources**: psychology, education, and career-related knowledge
- **Dialogue management**: multi-turn state tracking and strategy control
- **Safety mechanisms**: filtering, privacy protection, and referral triggers for crisis expressions

> Note: the original materials described the solution direction, but did not include a fully reproducible backend implementation or all DingTalk production settings.

![Technical Architecture](assets/07-technical-architecture.png)

*Technical architecture*

## 7. Completeness and Deliverables

The original project materials emphasized:

- a complete loop of recognition -> support -> suggestion -> follow-up
- interface design aligned with DingTalk UI patterns
- supporting documents, architecture diagrams, flowcharts, and testing materials

![Practicality Flow](assets/06-practicality-flow.png)

*Practicality and implementation flow*

![Service Loop](assets/08-service-closed-loop.png)

*Service closed-loop diagram*

## 8. Interface Preview

### 8.1 Platform View

![Platform Overview](assets/09-platform-overview.png)

### 8.2 Chat Example

![Chat Demo](assets/10-chat-demo.png)

## 9. Current GitHub Version

Compared with the original concept materials, the current repository additionally provides:

1. directly viewable Markdown docs and flowcharts
2. a locally runnable FastAPI service and web page
3. tests, CI, and runnable setup docs for continued development

High-priority next steps, if the project keeps evolving, include:

- integrating a fuller knowledge base or FAQ retrieval flow
- adding better risk keyword detection and referral logic
- storing conversation history and introducing richer state management
