**JARVIS 8.0 ULTRA**

AI Study Assistant for B.Sc Computer Science

Loyola Academy, Hyderabad

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**COMPLETE A-Z SYSTEM GUIDE**

Installation se lekar Exam tak ka poora safar

Platform: ROOTED Android + Termux

AI Engine: DeepSeek-R1:1.5B (Offline)

Algorithms: IRT + SM-2 + Psychological Engine

**GOAL: B.Sc Seat Confirmation**

**TABLE OF CONTENTS**

Yeh document A to Z samjhata hai ki JARVIS kaise kaam karta hai. Har
section ek specific topic cover karta hai.

  -----------------------------------------------------------------------
  **Section**             **Topic**               **Description**
  ----------------------- ----------------------- -----------------------
  1                       System Overview         JARVIS kya hai aur
                                                  kaise kaam karta hai

  2                       Installation Guide      Termux, llama.cpp,
                                                  DeepSeek setup

  3                       First Day Setup         Profile creation aur
                                                  diagnostic test

  4                       Daily Routine           Subah se raat tak ka
                                                  complete schedule

  5                       Study Session Flow      Question solve karne ka
                                                  process

  6                       IRT Adaptive Testing    Smart question
                                                  selection algorithm

  7                       Spaced Repetition       Kab aur kaise revise
                                                  karein

  8                       Psychological Engine    Motivation aur
                                                  gamification system

  9                       Root Commands           Distraction blocking
                                                  features

  10                      90-Day Study Plan       Complete preparation
                                                  roadmap

  11                      Interview Preparation   Day 31 se interview
                                                  practice

  12                      Mock Tests              Exam simulation
                                                  strategy

  13                      Exam Day Strategy       Final preparation tips

  14                      Troubleshooting         Common problems aur
                                                  solutions
  -----------------------------------------------------------------------

**SECTION 1: SYSTEM OVERVIEW**

**1.1 JARVIS Kya Hai?**

JARVIS ek AI-powered study assistant hai jo aapko B.Sc Computer Science
entrance exam ke liye prepare karta hai. Yeh system aapke ROOTED Android
phone pe Termux ke through chalta hai aur completely offline kaam karta
hai.

**Key Features:**

-   Adaptive Testing (IRT): Har question aapki ability ke hisaab se
    select hota hai

-   Spaced Repetition (SM-2): Topics ko scientifically revise karta hai

-   Local AI (DeepSeek-R1:1.5B): Questions generate karta hai - NO
    internet needed

-   Root Commands: Distracting apps ko automatically block karta hai

-   Psychological Engine: XP, streaks, achievements se motivate karta
    hai

-   Interview Prep: Day 31 se interview practice start karta hai

**1.2 Exam Pattern - Loyola Academy**

  -----------------------------------------------------------------------
  **Subject**       **Questions**     **Marks**         **Time**
  ----------------- ----------------- ----------------- -----------------
  Mathematics       20                20                20 min

  Physics           15                15                15 min

  Chemistry         10                10                10 min

  English           5                 5                 5 min

  TOTAL             50                50                50 min
  -----------------------------------------------------------------------

Important: Negative marking NAHI hai. Isliye har question attempt karna
chahiye.

**1.3 Selection Process**

Selection do stages me hoti hai: Written Exam (70%) + Interview (30%).
Interview MANDATORY hai aur kam se kam ek parent ka hona zaroori hai.

**Competition Stats:**

-   Total Applicants: 3,000-5,000 per year

-   Total Seats: 60-80 (B.Sc CS)

-   Competition Ratio: \~1:50

-   Expected Cut-off: 35-40/50 (General category)

**SECTION 2: INSTALLATION GUIDE**

**2.1 Requirements**

  -----------------------------------------------------------------------
  **Requirement**         **Minimum**             **Recommended**
  ----------------------- ----------------------- -----------------------
  Android Version         9.0 (Pie)               11.0+

  RAM                     4 GB                    6+ GB

  Storage                 4 GB free               8 GB free

  Root Access             Required                Magisk preferred

  Internet                For setup only          WiFi for downloads
  -----------------------------------------------------------------------

**2.2 Step-by-Step Installation**

**Step 1: Termux Install Karein**

1.  F-Droid app download karein: https://f-droid.org

2.  F-Droid me \'Termux\' search karein

3.  Termux install karein (Play Store se NAHI - wo outdated hai)

4.  Termux:API aur Termux:Boot bhi install karein

**Step 2: Termux Setup**

> pkg update && pkg upgrade -y
>
> pkg install git cmake clang wget python -y
>
> pkg install root-repo tsu -y

**Step 3: llama.cpp Build Karein**

Ollama Android pe directly nahi chalta, isliye llama.cpp use karte hain:

> git clone https://github.com/ggml-org/llama.cpp
>
> cd llama.cpp
>
> cmake -B build && cmake \--build build \--config Release -j\$(nproc)

**Step 4: DeepSeek Model Download Karein**

Q4_K_M quantized model (\~1.07 GB) download karein:

> mkdir -p \~/models
>
> wget -O \~/models/deepseek-q4.gguf
> \'https://huggingface.co/\.../deepseek-1.5b-q4.gguf\'

**Step 5: JARVIS Code Download Karein**

> git clone https://github.com/your-repo/jarvis
>
> cd jarvis
>
> pip install -r requirements.txt
>
> python setup.py

**2.3 Verify Installation**

> \# Check root access
>
> su -c \'id\'
>
> \# Output: uid=0(root) gid=0(root)
>
> \# Test AI model
>
> ./llama-cli -m \~/models/deepseek-q4.gguf -p \'Hello\'

**2.4 Storage Structure**

Installation ke baad folder structure:

> \~/jarvis/
>
> ├── data/ \# SQLite database
>
> ├── models/ \# AI models
>
> ├── cache/ \# Response cache
>
> ├── logs/ \# Application logs
>
> ├── backup/ \# Auto backups
>
> ├── jarvis.py \# Main application
>
> └── config.json \# Configuration

**SECTION 3: FIRST DAY SETUP**

**3.1 Application Start**

Pehli baar JARVIS start karne pe:

> python jarvis.py

Yeh aapko welcome screen dikhayega aur kuch basic questions puchega.

**3.2 Student Profile Setup**

JARVIS aapse ye information mangega:

  -----------------------------------------------------------------------
  **Field**               **Example**             **Purpose**
  ----------------------- ----------------------- -----------------------
  Name                    Rahul Kumar             Personalization

  Target College          Loyola Academy          Syllabus customization

  Exam Date               15 June 2025            Study plan calculation

  12th Percentage         85%                     Baseline assessment

  Strongest Subject       Mathematics             Initial theta estimate

  Weakest Subject         Physics                 Focus area
                                                  identification
  -----------------------------------------------------------------------

**3.3 Diagnostic Test**

Profile ke baad, JARVIS ek 20-question diagnostic test lega:

-   Mathematics: 8 questions (various topics)

-   Physics: 6 questions

-   Chemistry: 4 questions

-   English: 2 questions

Is test ka purpose: Initial theta (ability) score calculate karna.

**3.4 Initial Theta Calculation**

Diagnostic test ke baad, JARVIS har subject ke liye initial theta
calculate karega:

  -----------------------------------------------------------------------
  **Subject**       **Questions       **Initial Theta** **Ability Level**
                    Correct**                           
  ----------------- ----------------- ----------------- -----------------
  Mathematics       6/8               +0.5              Above Average

  Physics           3/6               -0.3              Below Average

  Chemistry         2/4               0.0               Average

  English           1/2               0.0               Average
  -----------------------------------------------------------------------

Theta range: -3 (very low) to +3 (very high). 0 = average ability.

**3.5 90-Day Plan Generation**

Diagnostic test ke results ke basis pe, JARVIS automatically 90-day
study plan generate karega:

-   Phase 1 (Day 1-30): Foundation - NCERT completion

-   Phase 2 (Day 31-60): Practice - 500+ problems per subject

-   Phase 3 (Day 61-80): Mastery - 15+ mock tests

-   Phase 4 (Day 81-90): Revision - Final preparation

**3.6 First Day Summary**

First day ke end tak, aapke paas ye hoga:

-   Complete student profile

-   Initial theta scores (har subject ke liye)

-   Weak/strong area identification

-   90-day personalized study plan

-   Daily schedule template

-   XP: 100 (Welcome bonus)

**SECTION 4: DAILY ROUTINE**

**4.1 Morning Routine (6:00 AM - 9:00 AM)**

**6:00 AM - Wake Up & Start**

-   Termux open karein

-   JARVIS automatically start: python jarvis.py \--auto

-   Wake lock activate: termux-wake-lock

-   Motivational message: \'Good morning! 94 days to exam. You got
    this!\'

**6:05 AM - Daily Goal Setting**

JARVIS aapko daily goals dikhayega:

> TODAY\'S GOALS (Day 12 of 90)
>
> □ Mathematics: 20 questions
>
> □ Physics: 15 questions
>
> □ Chemistry: 10 questions
>
> □ Revision: Quadratic Equations
>
> □ Mock Test: Mini (15 min)
>
> Streak: 12 days \| XP: 2,450 (Level 5)

**7:00 AM - 9:00 AM - Mathematics Session**

Morning time best hai Mathematics ke liye (fresh mind):

-   2-hour session

-   Pomodoro: 25 min study + 5 min break

-   Target: 20 questions

-   XP per question: 10 (correct), 5 (wrong with review)

**4.2 Mid-Morning (9:30 AM - 11:30 AM)**

**9:30 AM - Physics Session**

-   1.5 hour session

-   Focus on weak areas (based on theta)

-   Formula revision included

**11:30 AM - Chemistry Session**

-   1 hour session

-   Reaction mechanisms, periodic table

**4.3 Afternoon (2:00 PM - 5:00 PM)**

**2:00 PM - Practice Session**

-   Mixed subject practice

-   Speed drills: 20 questions in 15 minutes

**3:30 PM - Revision**

-   Spaced repetition topics

-   Flashcard review

**4:30 PM - Mini Mock Test**

-   15-minute mini test

-   Immediate feedback

**4.4 Evening (7:00 PM - 9:00 PM)**

**7:00 PM - Interview Prep (Day 31+)**

-   2 mock interview questions

-   AI feedback on answers

**8:30 PM - Daily Summary**

> DAILY SUMMARY - Day 12
>
> Questions Solved: 65/65 \| Accuracy: 87%
>
> Time: 4h 32m \| XP Earned: +340
>
> Streak: 12 days \| Theta: Maths +0.52, Physics -0.25

**4.5 Night (9:00 PM - 10:00 PM)**

**9:00 PM - Review & Planning**

-   Tomorrow\'s preview

-   Data backup (automatic)

-   Sleep reminder: \'Early sleep = better retention!\'

**10:00 PM - System Shutdown**

-   Wake lock release: termux-wake-unlock

-   Background service continues for backup

-   Next day alarm reminder

**SECTION 5: STUDY SESSION FLOW**

**5.1 Session Start**

Jab aap study session start karte ho:

1.  Subject select karein (Maths/Physics/Chemistry/English)

2.  Session type choose karein (Practice/Revision/Mock)

3.  Duration set karein (default: 25 min Pomodoro)

4.  Focus Mode activate (distracting apps blocked)

**5.2 Question Selection Process**

JARVIS IRT (Item Response Theory) use karke smart question selection
karta hai:

**Selection Criteria:**

-   Maximum Fisher Information: Question jo aapki ability ko best
    measure kare

-   Theta proximity: Question difficulty ≈ aapki current theta

-   Topic coverage: Har topic se balanced questions

-   Time since last attempt: Repeated questions avoid kare

**5.3 Question Display**

> MATHEMATICS - Question 15/20
>
> Topic: Quadratic Equations \| Difficulty: Medium (b = 0.3)
>
> If x² - 5x + 6 = 0, find sum of squares of roots.
>
> A\) 13 B) 25 C) 10 D) 9
>
> Time: 0:45 \| XP: 10

**5.4 Answer Submission**

Answer submit karne ke baad:

-   Immediate feedback (Correct/Wrong)

-   Detailed explanation

-   Theta update calculation

-   XP reward/penalty

**5.5 Theta Update**

Har question ke baad theta update hota hai:

> θ_new = θ_old + (observed - expected) / √information

Example:

-   Current theta: +0.5

-   Question difficulty (b): 0.3

-   Expected probability: 62%

-   Result: Correct (observed = 1)

-   New theta: 0.5 + (1 - 0.62) / √0.8 = +0.92

**5.6 Session End**

Session complete hone pe:

> SESSION COMPLETE!
>
> Questions: 20/20 \| Correct: 17 (85%) \| Time: 22:35
>
> XP Earned: +185 \| Bonus (Speed): +20 \| Bonus (Accuracy): +30
>
> TOTAL: +235 XP \| Theta Change: +0.45 → +0.52

**SECTION 6: IRT ADAPTIVE TESTING**

**6.1 IRT Kya Hai?**

IRT (Item Response Theory) ek scientific method hai jo har student ki
ability ko accurately measure karta hai. Traditional exams me sabko same
questions milte hain, lekin IRT me questions aapki ability ke hisaab se
adjust hote hain.

**6.2 IRT Parameters**

  -----------------------------------------------------------------------
  **Parameter**     **Symbol**        **Meaning**       **Range**
  ----------------- ----------------- ----------------- -----------------
  Difficulty        b                 Question kitna    -3 to +3
                                      mushkil hai       

  Discrimination    a                 Question kitna    0.5 to 2.5
                                      differentiate     
                                      karta hai         

  Guessing          c                 Random guess se   0.2 to 0.25
                                      correct hone ki   
                                      probability       
  -----------------------------------------------------------------------

**6.3 Theta (θ) - Ability Score**

Theta aapki ability represent karta hai:

  -----------------------------------------------------------------------
  **Theta Value**   **Percentile**    **Ability Level** **Expected
                                                        Score**
  ----------------- ----------------- ----------------- -----------------
  -3.0              0.1%              Very Low          \~5/50

  -1.0              15.9%             Below Average     \~25/50

  0.0               50%               Average           \~35/50

  +1.0              84.1%             Above Average     \~42/50

  +2.0              97.7%             High              \~47/50

  +3.0              99.9%             Very High         \~49/50
  -----------------------------------------------------------------------

**6.4 Question Selection Algorithm**

JARVIS har question ke liye ye process follow karta hai:

1.  Available questions ka Fisher Information calculate karein

2.  Maximum information wala question select karein

3.  Question display karein

4.  Response collect karein

5.  Theta update karein

6.  Stopping rule check karein (SE \< 0.3)

**6.5 Fisher Information**

Fisher Information batata hai ki question kitna informative hai:

> I(θ) = D² × a² × (1-c)² × P × Q / (P-c)²

Maximum information tab milti hai jab question difficulty (b) ≈ student
theta (θ)

**6.6 Stopping Rules**

Test kab khatam hoga? Ye decide karne ke rules:

-   Standard Error \< 0.3 (precise measurement)

-   Minimum 10 questions (reliable estimate)

-   Maximum 30 questions (time limit)

-   Theta stabilization (last 5 questions me \< 0.1 change)

**6.7 Practical Example**

Let\'s say aapka current theta = +0.5 hai:

  -----------------------------------------------------------------------
  **Question**      **Difficulty      **Information**   **Selected?**
                    (b)**                               
  ----------------- ----------------- ----------------- -----------------
  Q1                -1.0 (Easy)       0.3               No

  Q2                +0.5 (Match)      0.9               Yes!

  Q3                +1.5 (Hard)       0.5               No

  Q4                0.0 (Medium)      0.7               No
  -----------------------------------------------------------------------

Q2 select hoga kyunki uski Fisher Information sabse zyada hai.

**SECTION 7: SPACED REPETITION (SM-2)**

**7.1 SM-2 Algorithm Kya Hai?**

SM-2 ek scientifically proven algorithm hai jo batata hai ki aapko kisi
topic ko kab revise karna chahiye. Yeh Ebbinghaus Forgetting Curve pe
based hai - hum quickly forget karte hain, lekin timely revision se
memory strong hoti hai.

**7.2 Quality Scale**

Har revision ke baad aapko apni recall quality rate karni hai:

  -----------------------------------------------------------------------
  **Quality**             **Meaning**             **Action**
  ----------------------- ----------------------- -----------------------
  5                       Perfect - Instant       Interval increase
                          recall                  

  4                       Good - Some hesitation  Interval increase

  3                       Pass - Difficult but    Small interval increase
                          correct                 

  2                       Fail - Incorrect but    Reset to short interval
                          recognized              

  1                       Fail - No recall        Reset to learning phase

  0                       Complete blackout       Start from scratch
  -----------------------------------------------------------------------

**7.3 Interval Calculation**

Review intervals kaise calculate hote hain:

  -----------------------------------------------------------------------
  **Review \#**           **Quality ≥ 4**         **Quality \< 4**
  ----------------------- ----------------------- -----------------------
  1st Review              1 day                   1 day

  2nd Review              6 days                  3 days

  3rd Review              6 × EF                  Reset

  4th Review              Previous × EF           Reset

  nth Review              Previous × EF           Reset
  -----------------------------------------------------------------------

EF = Ease Factor (default 2.5, minimum 1.3)

**7.4 Ease Factor Update**

> EF_new = EF_old + (0.1 - (5 - quality) × (0.08 + (5 - quality) ×
> 0.02))

Examples:

-   Quality 5: EF increases by 0.10 → New EF = 2.60

-   Quality 4: EF increases by 0.02 → New EF = 2.52

-   Quality 3: EF decreases by 0.14 → New EF = 2.36

-   Quality 0: EF decreases by 0.80 → New EF = 1.70

**7.5 Practical Schedule Example**

Topic: Quadratic Equations

  --------------------------------------------------------------------------
  **Date**       **Review \#**  **Quality**    **Next         **Notes**
                                               Review**       
  -------------- -------------- -------------- -------------- --------------
  Day 1          1st            4              Day 2          First learning

  Day 2          2nd            5              Day 8          Good recall

  Day 8          3rd            4              Day 20         EF = 2.52

  Day 20         4th            5              Day 51         EF = 2.62

  Day 51         5th            4              Day 130        EF = 2.64
  --------------------------------------------------------------------------

**7.6 Daily Revision Queue**

Har subah JARVIS aapko revision queue dikhata hai:

> TODAY\'S REVISION QUEUE
>
> OVERDUE (2): Trigonometry Identities, Newton\'s Laws
>
> DUE TODAY (3): Quadratic Equations, Chemical Bonding, English Grammar
>
> UPCOMING (5): Tomorrow: Calculus, Day after: Thermodynamics

**SECTION 8: PSYCHOLOGICAL ENGINE**

**8.1 Motivation Science**

JARVIS teen scientifically proven psychological techniques use karta
hai:

**1. Loss Aversion**

Research: Losses feel 2x more painful than equivalent gains (Kahneman &
Tversky, 1979)

-   Messaging: \'Don\'t LOSE your 12-day streak!\' instead of \'Keep
    your streak\'

-   Warning: \'Skipping today costs you 150 XP!\'

-   Loss Aversion Multiplier: 2.0x

**2. Variable Reward System**

Unpredictable rewards trigger more dopamine (like slot machines):

  -----------------------------------------------------------------------
  **Reward Type**   **Probability**   **XP Bonus**      **Other**
  ----------------- ----------------- ----------------- -----------------
  Normal            55%               Base XP           ---

  Small Bonus       25%               1.2x XP           ---

  Bonus             15%               1.5x XP           2x coins

  Jackpot           5%                3x XP             5x coins

  Legendary         0.1%              10x XP            Rare achievement
  -----------------------------------------------------------------------

**3. Social Comparison**

-   Leaderboards: Daily, Weekly, Monthly, All-time

-   Percentile display: \'You\'re in TOP 5%\'

-   Motivational comparison: \'Rahul solved 500 questions today!\'

**8.2 XP System**

  -----------------------------------------------------------------------
  **Activity**                        **XP Reward**
  ----------------------------------- -----------------------------------
  Correct answer                      +10 XP

  Wrong answer (with review)          +5 XP

  Wrong answer (skip review)          +0 XP

  Complete daily goals                +50 XP

  Maintain streak (per day)           +10 XP

  Mock test completion                +100 XP

  New topic mastered                  +200 XP

  Achievement unlock                  +50 to +500 XP
  -----------------------------------------------------------------------

**8.3 Streak System**

Streak motivation:

-   Daily login streak (consecutive days)

-   Study streak (consecutive study sessions)

-   Accuracy streak (consecutive correct answers)

-   Streak freeze available (3 free per month)

-   Recovery window: 24 hours to save streak

**8.4 Level System**

  -----------------------------------------------------------------------
  **Level**         **Title**         **XP Required**   **Rewards**
  ----------------- ----------------- ----------------- -----------------
  1                 Beginner          0                 Basic features

  5                 Learner           2,000             Custom themes

  10                Student           5,000             Priority support

  15                Scholar           10,000            Advanced
                                                        analytics

  20                Master            20,000            All achievements
  -----------------------------------------------------------------------

**8.5 Achievements**

  -----------------------------------------------------------------------
  **Achievement**         **Requirement**         **XP**
  ----------------------- ----------------------- -----------------------
  First Steps             Complete 10 questions   50

  Century                 Complete 100 questions  100

  Speed Demon             20 questions in 15 min  150

  Perfectionist           100% accuracy in        200
                          session                 

  Marathon                Study 4 hours straight  300

  Mock Master             Score 45+ in mock test  500
  -----------------------------------------------------------------------

**SECTION 9: ROOT COMMANDS**

**9.1 Root Access Setup**

JARVIS root access use karta hai distraction blocking ke liye:

> \# Check root access
>
> su -c \'id\'
>
> \# Output: uid=0(root) gid=0(root)

**9.2 Distraction Blocking Commands**

  -----------------------------------------------------------------------
  **Action**                          **Command**
  ----------------------------------- -----------------------------------
  Force stop app                      su -c \'am force-stop
                                      com.instagram.android\'

  Disable app                         su -c \'pm disable
                                      com.instagram.android\'

  Enable app                          su -c \'pm enable
                                      com.instagram.android\'

  Clear app data                      su -c \'pm clear
                                      com.instagram.android\'

  Block network                       su -c \'iptables -A OUTPUT -d IP -j
                                      DROP\'
  -----------------------------------------------------------------------

**9.3 Focus Mode**

Focus Mode activate karne pe:

1.  Distracting apps list load hoti hai (89 apps pre-configured)

2.  Selected apps force-stop ho jate hain

3.  Network blocking activate (optional)

4.  Background monitoring start (foreground app check)

5.  Focus session timer start

**9.4 Distracting Apps List**

Pre-configured distracting apps (categories):

-   Social Media: Instagram, Facebook, Twitter, Snapchat, TikTok

-   Entertainment: YouTube, Netflix, Prime Video, Hotstar

-   Gaming: PUBG, Free Fire, COD Mobile, Clash of Clans

-   Shopping: Amazon, Flipkart, Myntra

-   Messaging: WhatsApp (optional), Telegram (optional)

**9.5 Foreground App Monitoring**

Background service har 1 second me check karta hai:

> su -c \'dumpsys activity activities \| grep mResumedActivity\'

If distracting app detected:

1.  Warning notification (first time)

2.  App force-stop (second time)

3.  XP penalty: -20 XP

4.  Streak risk warning

**9.6 Wake Lock Management**

> \# Acquire wake lock (keep CPU running)
>
> termux-wake-lock
>
> \# Release wake lock (save battery)
>
> termux-wake-unlock

Wake lock automatically manage hota hai based on study session.

**9.7 Battery Optimization**

Root access se battery optimization:

-   Background apps kill (save RAM and battery)

-   CPU governor set to \'conservative\' during study

-   Network optimization (block unnecessary connections)

-   Display brightness auto-adjust

**SECTION 10: 90-DAY STUDY PLAN**

**10.1 Phase Overview**

  -----------------------------------------------------------------------
  **Phase**         **Days**          **Focus**         **Target Score**
  ----------------- ----------------- ----------------- -----------------
  Foundation        1-30              NCERT completion, 30+/50
                                      basics            

  Practice          31-60             500+ problems per 35+/50
                                      subject           

  Mastery           61-80             15+ mock tests,   40+/50
                                      speed             

  Revision          81-90             Final revision,   45+/50
                                      confidence        
  -----------------------------------------------------------------------

**10.2 Phase 1: Foundation (Day 1-30)**

**Goals:**

-   Complete NCERT for all subjects

-   Create formula sheets

-   Identify strengths and weaknesses

-   Build study habits

-   Establish baseline theta

**Weekly Breakdown:**

  -------------------------------------------------------------------------------
  **Week**       **Mathematics**   **Physics**    **Chemistry**   **English**
  -------------- ----------------- -------------- --------------- ---------------
  1              Algebra basics    Mechanics      Mole concept    Grammar

  2              Quadratic eq.     Motion         Atomic          Vocabulary
                                                  structure       

  3              Trigonometry      Newton\'s laws Bonding         Comprehension

  4              Coordinate geo.   Work & Energy  States of       Practice
                                                  matter          
  -------------------------------------------------------------------------------

**10.3 Phase 2: Practice (Day 31-60)**

**Goals:**

-   500+ problems per subject

-   Weekly mock tests

-   Focus on high-weightage topics

-   Interview preparation start (Day 31)

-   Speed building exercises

**Subject Distribution:**

-   Mathematics: 40% time (highest weightage)

-   Physics: 30% time

-   Chemistry: 20% time

-   English: 10% time

**10.4 Phase 3: Mastery (Day 61-80)**

**Goals:**

-   15+ full mock tests

-   80%+ accuracy target

-   Speed: 1 question/minute

-   Weak area elimination

-   Interview mock sessions

**10.5 Phase 4: Revision (Day 81-90)**

**Goals:**

-   Daily formula revision

-   Daily mock tests

-   Stress management

-   Confidence building

-   No new topics

**10.6 Daily Study Hours**

  -----------------------------------------------------------------------
  **Time Slot**           **Duration**            **Activity**
  ----------------------- ----------------------- -----------------------
  7:00-9:00 AM            2 hours                 Mathematics

  9:30-11:00 AM           1.5 hours               Physics

  11:30 AM-12:30 PM       1 hour                  Chemistry

  2:00-3:00 PM            1 hour                  English/Revision

  3:15-4:45 PM            1.5 hours               Practice

  7:00-8:00 PM            1 hour                  Interview Prep

  TOTAL                   8 hours                 Daily study
  -----------------------------------------------------------------------

**SECTION 11: INTERVIEW PREPARATION**

**11.1 Interview Requirements**

Loyola Academy me interview MANDATORY hai:

-   At least one parent MUST attend

-   Weightage: Written (70%) + Interview (20%) + 12th marks (10%)

-   Duration: 15-20 minutes

-   Panel: 2-3 faculty members

**11.2 Question Categories**

  -----------------------------------------------------------------------
  **Category**            **Questions**           **Weightage**
  ----------------------- ----------------------- -----------------------
  Personal                Tell me about yourself, 25%
                          hobbies, goals          

  Academic                Why B.Sc CS? Why        30%
                          Loyola? Subjects        

  CS Basics               Programming, computers, 20%
                          technology              

  Current Affairs         AI, Digital India, tech 15%
                          news                    

  Situational             Problem-solving         10%
                          scenarios               
  -----------------------------------------------------------------------

**11.3 Common Questions & Ideal Answers**

**Q: Tell me about yourself**

Ideal Answer Structure:

-   Background: Name, place, family brief

-   Education: 12th subjects, percentage

-   Interests: Relevant hobbies (coding, tech)

-   Goals: Why B.Sc CS, career plans

-   Time: 1-2 minutes max

**Q: Why B.Sc Computer Science?**

Key Points:

-   Genuine interest in technology

-   Career goals in IT/software

-   Specific examples of projects/learning

-   Why not B.Tech (if applicable)

**Q: Why Loyola Academy?**

Research these points:

-   College reputation and rankings

-   Faculty quality

-   Placement records

-   Campus facilities

-   Alumni achievements

**11.4 Parent Interview Questions**

Common questions for parents:

1.  What are your expectations from this institution?

2.  How involved are you in your child\'s education?

3.  How will you support your child academically?

4.  What are your financial plans for education?

5.  Any specific concerns about your child?

**11.5 Interview Practice with JARVIS**

Day 31 se daily interview practice:

-   2 mock questions per day

-   AI evaluates your answer

-   Feedback on content, confidence, clarity

-   Recording option for self-review

-   Progress tracking over time

**11.6 Interview Day Tips**

-   Dress formally (formal shirt, trousers)

-   Arrive 30 minutes early

-   Carry all documents in file

-   Be confident, maintain eye contact

-   Listen carefully, answer precisely

-   Don\'t lie or exaggerate

-   Ask intelligent questions at the end

**SECTION 12: MOCK TESTS**

**12.1 Mock Test Types**

  -----------------------------------------------------------------------
  **Type**          **Questions**     **Time**          **Purpose**
  ----------------- ----------------- ----------------- -----------------
  Mini Test         15                15 min            Quick practice

  Subject Test      25                25 min            Subject focus

  Full Mock         50                50 min            Exam simulation

  Previous Year     50                50 min            Pattern practice
  -----------------------------------------------------------------------

**12.2 Mock Test Schedule**

  -----------------------------------------------------------------------
  **Phase**         **Full Mocks**    **Subject Tests** **Mini Tests**
  ----------------- ----------------- ----------------- -----------------
  Phase 1           1/week            3/week            Daily

  Phase 2           2/week            6/week            Daily

  Phase 3           3/week            6/week            2/day

  Phase 4           Daily             2/day             2/day
  -----------------------------------------------------------------------

**12.3 Mock Test Flow**

1.  Select test type (Full/Subject/Mini)

2.  Focus mode activate (distractions blocked)

3.  Timer start (50 min for full mock)

4.  Questions display one by one

5.  Submit/Review options available

6.  Auto-submit when time ends

**12.4 Result Analysis**

> MOCK TEST RESULTS - Test #12
>
> Score: 42/50 (84%) \| Time: 47:32 (2:28 remaining)
>
> Mathematics: 17/20 (85%) \| Physics: 12/15 (80%)
>
> Chemistry: 9/10 (90%) \| English: 4/5 (80%)
>
> Theta: Maths +0.55, Physics -0.20 \| XP: +250

**12.5 Error Analysis**

Har mock test ke baad detailed error analysis:

-   Wrong answers ka topic-wise breakdown

-   Mistake type (conceptual/calculation/silly)

-   Time spent on each question

-   Improvement suggestions

-   Practice recommendations

**SECTION 13: EXAM DAY STRATEGY**

**13.1 Day Before Exam**

-   Light revision only (formulas, key concepts)

-   Documents ready: Admit card, ID proof, photographs

-   Early dinner (8 PM)

-   Early sleep (9:30 PM)

-   Phone charge karein

-   Clothes ready karein

**13.2 Exam Morning**

  -----------------------------------------------------------------------
  **Time**                            **Activity**
  ----------------------------------- -----------------------------------
  6:00 AM                             Wake up, freshen up

  7:00 AM                             Light breakfast

  7:30 AM                             Final document check

  8:00 AM                             Leave for center

  9:00 AM                             Reach center (30 min early)

  9:30 AM                             Enter examination hall
  -----------------------------------------------------------------------

**13.3 Time Management During Exam**

50 minutes me 50 questions:

  -----------------------------------------------------------------------
  **Phase**               **Time**                **Activity**
  ----------------------- ----------------------- -----------------------
  First Pass              0-35 min                Answer confident
                                                  questions

  Second Pass             35-45 min               Return to skipped
                                                  questions

  Review                  45-50 min               Review and fill blanks
  -----------------------------------------------------------------------

**13.4 Question Attempt Strategy**

**45-Second Rule:**

Agar 45 seconds me progress nahi ho rahi → SKIP!

**Order of Attempt:**

1.  Start with your STRONGEST subject

2.  Within each subject, do EASY questions first

3.  Complete sections in confidence order

4.  Return to skipped questions in second pass

5.  Fill ALL blanks (no negative marking!)

**13.5 Last 5 Minutes**

-   0:00-2:00: Review marked questions

-   2:00-3:30: Fill unanswered using elimination

-   3:30-4:30: Fill remaining with single option

-   4:30-5:00: Verify all bubbles filled

**13.6 Stress Management**

**If You Panic:**

-   STOP immediately

-   Take 3 deep breaths (4-7-8 technique)

-   Remind yourself: \'I am prepared\'

-   Continue with next question

-   Don\'t dwell on tough questions

**SECTION 14: TROUBLESHOOTING**

**14.1 Installation Issues**

**Problem: Termux not getting root access**

-   Solution: Check if Magisk is properly installed

-   Command: su -c \'id\' should show uid=0

-   Grant root permission in Magisk app

**Problem: Model download fails**

-   Solution: Check internet connection

-   Try alternative mirror links

-   Use wget with retry: wget -c \--tries=10

**14.2 Performance Issues**

**Problem: AI responses too slow**

-   Solution: Check available RAM

-   Close other apps

-   Use lower quantization (Q3_K_M)

-   Clear cache: rm -rf \~/jarvis/cache/\*

**Problem: Battery draining fast**

-   Solution: Release wake lock when not studying

-   Reduce polling interval

-   Use battery saver mode

-   Run heavy tasks during charging

**14.3 Data Issues**

**Problem: Database corrupted**

-   Solution: Restore from backup

> cp \~/jarvis/backup/latest.db \~/jarvis/data/jarvis.db

**Problem: Lost streak due to app crash**

-   Solution: Use streak freeze (if available)

-   Contact support within 24 hours

**14.4 Common Errors**

  -----------------------------------------------------------------------
  **Error**               **Cause**               **Solution**
  ----------------------- ----------------------- -----------------------
  Permission denied       No root access          Grant root in Magisk

  Model not found         Wrong path              Check \~/models/ folder

  Out of memory           Low RAM                 Close apps, use swap

  Connection failed       No internet             Check WiFi/data

  Session timeout         Inactivity              Restart session
  -----------------------------------------------------------------------

**14.5 Emergency Recovery**

Agar kuch bhi kaam nahi kar raha:

1.  Backup current data: tar -czf backup.tar.gz \~/jarvis

2.  Reinstall: git clone \... && pip install -r requirements.txt

3.  Restore data: tar -xzf backup.tar.gz

4.  Contact support with error logs

**14.6 Support Contact**

-   Email: support@jarvis-ai.local

-   GitHub Issues: github.com/your-repo/jarvis/issues

-   Discord: discord.gg/jarvis-community

-   Response time: 24-48 hours

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**GOAL: B.Sc SEAT CONFIRMATION**

90 Days × 8 Hours × Focused Effort = Success

*JARVIS is with you every step of the way!*

Document generated by JARVIS AI Research Team

Version 8.0 ULTRA
