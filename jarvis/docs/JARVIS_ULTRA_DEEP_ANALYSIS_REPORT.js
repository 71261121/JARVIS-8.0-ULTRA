const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, 
        Header, Footer, AlignmentType, PageOrientation, LevelFormat, 
        HeadingLevel, BorderStyle, WidthType, ShadingType, VerticalAlign, 
        PageNumber, PageBreak } = require('docx');
const fs = require('fs');

// Color scheme - "Midnight Code" for AI/Tech project
const colors = {
  primary: "020617",      // Midnight Black
  body: "1E293B",         // Deep Slate Blue
  secondary: "64748B",    // Cool Blue-Gray
  accent: "94A3B8",       // Steady Silver
  tableBg: "F8FAFC",      // Glacial Blue-White
  danger: "DC2626",       // Red for warnings
  success: "16A34A",      // Green for success
  warning: "D97706"       // Orange for warnings
};

const tableBorder = { style: BorderStyle.SINGLE, size: 12, color: colors.primary };
const cellBorders = { top: tableBorder, bottom: tableBorder, left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE } };

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Times New Roman", size: 24 } } },
    paragraphStyles: [
      { id: "Title", name: "Title", basedOn: "Normal",
        run: { size: 56, bold: true, color: colors.primary, font: "Times New Roman" },
        paragraph: { spacing: { before: 240, after: 120 }, alignment: AlignmentType.CENTER } },
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 36, bold: true, color: colors.primary, font: "Times New Roman" },
        paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, color: colors.body, font: "Times New Roman" },
        paragraph: { spacing: { before: 280, after: 160 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, color: colors.secondary, font: "Times New Roman" },
        paragraph: { spacing: { before: 200, after: 120 }, outlineLevel: 2 } }
    ]
  },
  numbering: {
    config: [
      { reference: "bullet-list",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbered-list-1",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbered-list-2",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbered-list-3",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbered-list-4",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbered-list-5",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbered-list-6",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbered-list-7",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] }
    ]
  },
  sections: [
    // COVER PAGE
    {
      properties: {
        page: { margin: { top: 0, right: 0, bottom: 0, left: 0 } }
      },
      children: [
        new Paragraph({ spacing: { before: 6000 }, children: [] }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "JARVIS 8.0 ULTRA", bold: true, size: 72, color: colors.primary })]
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 400 },
          children: [new TextRun({ text: "DEEPEST PROJECT ANALYSIS REPORT", bold: true, size: 36, color: colors.secondary })]
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 200 },
          children: [new TextRun({ text: "RUTHLESS BEHAVIOUR DOMINATION SYSTEM", size: 28, color: colors.body })]
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 800 },
          children: [new TextRun({ text: "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", color: colors.accent })]
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 400 },
          children: [new TextRun({ text: "MODE: RUTHLESS", bold: true, size: 28, color: colors.danger })]
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 200 },
          children: [new TextRun({ text: "GOAL: LOYOLA COLLEGE SEAT CONFIRMATION", bold: true, size: 28, color: colors.success })]
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 200 },
          children: [new TextRun({ text: "PERMISSION: FULL BEHAVIOUR MONITORING", bold: true, size: 28, color: colors.warning })]
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 800 },
          children: [new TextRun({ text: "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", color: colors.accent })]
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 600 },
          children: [new TextRun({ text: "This is NOT an Engineering Demo", size: 24, color: colors.body, italics: true })]
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 100 },
          children: [new TextRun({ text: "This is an EXAM WEAPON", bold: true, size: 28, color: colors.primary })]
        }),
        new Paragraph({ children: [new PageBreak()] })
      ]
    },
    // MAIN CONTENT
    {
      properties: {
        page: { margin: { top: 1800, right: 1440, bottom: 1440, left: 1440 } }
      },
      headers: {
        default: new Header({ children: [new Paragraph({
          alignment: AlignmentType.RIGHT,
          children: [new TextRun({ text: "JARVIS 8.0 ULTRA - Deep Analysis Report", size: 18, color: colors.secondary, italics: true })]
        })] })
      },
      footers: {
        default: new Footer({ children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "Page ", size: 18 }), new TextRun({ children: [PageNumber.CURRENT], size: 18 }), new TextRun({ text: " of ", size: 18 }), new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 18 })]
        })] })
      },
      children: [
        // EXECUTIVE SUMMARY
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("EXECUTIVE SUMMARY")] }),
        new Paragraph({
          spacing: { before: 200, after: 200 },
          children: [new TextRun({ text: "This report represents a complete re-evaluation of the JARVIS project. After analyzing all previous blueprints, implementations, and the user's specific requirements, critical flaws have been identified that fundamentally undermine the project's core objective: ", size: 24 }), new TextRun({ text: "SEAT CONFIRMATION AT LOYOLA ACADEMY", bold: true, size: 24, color: colors.primary })]
        }),
        new Paragraph({
          spacing: { before: 200, after: 200 },
          children: [new TextRun({ text: "The previous implementation scored 45/100 because it prioritized technical elegance over exam success. A Next.js web application was built instead of a Termux TUI. Cloud APIs were used instead of local LLM. Root commands were simulated instead of executed. These decisions made several blueprint features architecturally impossible. This report provides a ruthless analysis of all flaws and presents a completely redesigned system philosophy focused exclusively on one outcome: ", size: 24 }), new TextRun({ text: "EXAM SUCCESS.", bold: true, size: 24, color: colors.success })]
        }),

        // PART 1: OLD PLAN FLAWS
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("PART 1: OLD PLAN FLAWS - COMPLETE ANALYSIS")] }),
        
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("1.1 The Fundamental Design Flaw")] }),
        new Paragraph({
          spacing: { before: 200, after: 200 },
          children: [new TextRun({ text: "The most critical flaw was not technical—it was philosophical. The previous system was designed as a ", size: 24 }), new TextRun({ text: "HELPER", bold: true, size: 24, color: colors.danger }), new TextRun({ text: " when the requirement was for a ", size: 24 }), new TextRun({ text: "CONTROLLER", bold: true, size: 24, color: colors.success }), new TextRun({ text: ". This distinction permeates every aspect of the system and explains why multiple features failed to meet requirements.", size: 24 })]
        }),
        
        // Helper vs Controller Table
        new Table({
          columnWidths: [4680, 4680],
          margins: { top: 100, bottom: 100, left: 180, right: 180 },
          rows: [
            new TableRow({
              tableHeader: true,
              children: [
                new TableCell({ borders: cellBorders, shading: { fill: colors.tableBg, type: ShadingType.CLEAR }, verticalAlign: VerticalAlign.CENTER,
                  children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "HELPER MINDSET (OLD)", bold: true, size: 22, color: colors.danger })] })] }),
                new TableCell({ borders: cellBorders, shading: { fill: colors.tableBg, type: ShadingType.CLEAR }, verticalAlign: VerticalAlign.CENTER,
                  children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "CONTROLLER MINDSET (REQUIRED)", bold: true, size: 22, color: colors.success })] })] })
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "User ko comfortable rakhna", size: 22 })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "User ko HONEST rakhna", size: 22 })] })] })
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Guide karna", size: 22 })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "JUDGE, INTERRUPT, PRESSURE karna", size: 22 })] })] })
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Motivational quotes dena", size: 22 })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Excuses TODNA", size: 22 })] })] })
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Polite suggestions", size: 22 })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Direct, HARSH, UNCOMFORTABLE statements", size: 22 })] })] })
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Wait for user to ask", size: 22 })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "BINA BULAYE BAAT KARNA", size: 22 })] })] })
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Features for features' sake", size: 22 })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Sirf EXAM SCORE improve karne wale features", size: 22 })] })] })
              ]
            })
          ]
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 100, after: 300 },
          children: [new TextRun({ text: "Table 1: Helper vs Controller Mindset Comparison", size: 20, color: colors.secondary, italics: true })]
        }),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("1.2 Platform Architecture Failure")] }),
        new Paragraph({
          spacing: { before: 200, after: 200 },
          children: [new TextRun({ text: "Blueprint specified: ROOTED ANDROID + TERMUX TUI. What was built: Next.js 16 Web Application. This single decision made multiple critical features impossible. Web applications cannot run 24/7 background services. They cannot access root commands. They cannot force-stop apps. They require internet. They suspend when the browser tab is inactive. The user's tablet will not have a browser tab open 24 hours a day.", size: 24 })]
        }),
        new Paragraph({
          spacing: { before: 200, after: 200 },
          children: [new TextRun({ text: "EXAM IMPACT: ", bold: true, size: 24, color: colors.danger }), new TextRun({ text: "Without 24/7 monitoring, distraction patterns cannot be detected. Without root access, distracting apps cannot be force-stopped. Without background services, the user can simply close the browser and escape accountability. This directly undermines seat confirmation.", size: 24 })]
        }),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("1.3 Root Command Simulation Failure")] }),
        new Paragraph({
          spacing: { before: 200, after: 200 },
          children: [new TextRun({ text: "The root-commands.ts file exists with 479 lines of code. Every command returns simulated success. Not a single command actually executes on the Android system. The forceStopApp() function logs to console and returns true. The blockNetwork() function does nothing. The acquireWakeLock() function cannot work from a web browser. This is not partial implementation—this is complete simulation of functionality that was architecturally impossible given the platform choice.", size: 24 })]
        }),
        new Paragraph({
          spacing: { before: 200, after: 200 },
          children: [new TextRun({ text: "EXAM IMPACT: ", bold: true, size: 24, color: colors.danger }), new TextRun({ text: "User's biggest distractions are Porn and Instagram. The system cannot block these. User can watch porn at 2 AM and the system will log 'Command simulated' instead of blocking access. This directly enables continued self-sabotage and undermines exam preparation.", size: 24 })]
        }),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("1.4 LLM Implementation Failure")] }),
        new Paragraph({
          spacing: { before: 200, after: 200 },
          children: [new TextRun({ text: "Blueprint specified: DeepSeek-R1:1.5B via Ollama/llama.cpp with Q4_K_M quantization (4GB compressed to 1GB), response caching in SQLite, pre-generated question banks overnight, target 2-5 second response time. What was built: Z.ai Cloud API. This is fundamentally different from the blueprint requirements. Every AI query now requires internet. Every query incurs API costs. There is no caching. There are no pre-generated question banks. The entire optimization strategy was discarded.", size: 24 })]
        }),
        new Paragraph({
          spacing: { before: 200, after: 200 },
          children: [new TextRun({ text: "EXAM IMPACT: ", bold: true, size: 24, color: colors.warning }), new TextRun({ text: "Moderate impact. Cloud API works for question generation, but requires internet connectivity. If user's internet fails during study session, the system becomes useless. Pre-generated question banks would have ensured uninterrupted practice regardless of connectivity.", size: 24 })]
        }),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("1.5 Behaviour Monitoring Absence")] }),
        new Paragraph({
          spacing: { before: 200, after: 200 },
          children: [new TextRun({ text: "The user explicitly stated: 8/10 comfort with AI control, willing to have ALL behaviour monitored. The old system had no capability to monitor app usage, screen unlocks, scroll behaviour, study avoidance patterns, sleep disruption, or dopamine crash indicators. The database has a DistractionEvent model, but no code populates it with real data. The system is blind to actual user behaviour.", size: 24 })]
        }),
        new Paragraph({
          spacing: { before: 200, after: 200 },
          children: [new TextRun({ text: "EXAM IMPACT: ", bold: true, size: 24, color: colors.danger }), new TextRun({ text: "Critical. User has history of inconsistency, burnout, and distraction patterns. Without behaviour monitoring, the system cannot detect when the user is falling into self-sabotage patterns. It cannot intervene proactively. It can only react after the damage is done.", size: 24 })]
        }),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("1.6 Psychological Engine Misalignment")] }),
        new Paragraph({
          spacing: { before: 200, after: 200 },
          children: [new TextRun({ text: "The psychological engine was implemented correctly in code (Loss Aversion, Variable Rewards, Leaderboards). However, it operates in HELPER mode. It rewards good behaviour but does not punish bad behaviour effectively. Loss messages are shown, but the user can ignore them. There is no external enforcement. The system assumes the user will feel guilt and self-correct. This assumption has been proven wrong by the user's history of inconsistency.", size: 24 })]
        }),
        new Paragraph({
          spacing: { before: 200, after: 200 },
          children: [new TextRun({ text: "EXAM IMPACT: ", bold: true, size: 24, color: colors.danger }), new TextRun({ text: "High. User's biggest fear is 'Right effort, wrong strategy.' The psychological engine should have been designed to prevent wrong effort through external enforcement, not rely on internal motivation that has historically failed.", size: 24 })]
        }),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("1.7 Exam Focus Dilution")] }),
        new Paragraph({
          spacing: { before: 200, after: 200 },
          children: [new TextRun({ text: "The project accumulated features without clear exam impact mapping. Interview preparation was implemented but not integrated into the 75-day study plan. Mock tests exist in schema but lack auto-generation logic. The 90-day plan has database models but no actual planning algorithm. Voice assistant features were discussed but add complexity without clear exam benefit. Technical obsession diluted exam focus.", size: 24 })]
        }),
        new Paragraph({
          spacing: { before: 200, after: 200 },
          children: [new TextRun({ text: "EXAM IMPACT: ", bold: true, size: 24, color: colors.danger }), new TextRun({ text: "Critical. Every feature that does not directly improve exam score is WASTED EFFORT. The user has 75 days. Every hour spent on non-essential features is an hour not spent on exam preparation. This is the opposite of ruthless efficiency.", size: 24 })]
        }),

        // PART 2: NEW RUTHLESS DESIGN PHILOSOPHY
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("PART 2: NEW RUTHLESS DESIGN PHILOSOPHY")] }),
        
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.1 Core Principle: SEAT CONFIRMATION IS THE ONLY METRIC")] }),
        new Paragraph({
          spacing: { before: 200, after: 200 },
          children: [new TextRun({ text: "Every feature, every line of code, every design decision must answer one question: DOES THIS IMPROVE THE PROBABILITY OF SEAT CONFIRMATION? If the answer is not a clear YES with measurable impact, the feature is rejected. No exceptions. No 'nice to have' features. No 'future enhancement' features. Only what directly contributes to exam success.", size: 24 })]
        }),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.2 The BEHAVIOUR DOMINATION Principle")] }),
        new Paragraph({
          spacing: { before: 200, after: 200 },
          children: [new TextRun({ text: "User behaviour ≠ User intention. The user WANTS to study. The user INTENDS to study 8 hours. But behaviour shows inconsistency, burnout, and distraction. The system must not trust intention. The system must measure, judge, and control behaviour. Data is truth. Self-report is unreliable. The system monitors everything: app usage, screen time, scroll patterns, sleep cycles, and study consistency. Decisions are made on DATA, not on what the user says.", size: 24 })]
        }),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.3 The EXTERNAL CONSCIENCE Principle")] }),
        new Paragraph({
          spacing: { before: 200, after: 200 },
          children: [new TextRun({ text: "The AI is not a friend. The AI is not a helper. The AI is an EXTERNAL CONSCIENCE. It has permission to: Speak without being prompted. Interrupt any activity. Make direct, harsh, uncomfortable statements. Confront mistakes immediately. Call out lies and excuses. The user gave explicit permission for this level of control (8/10 comfort rating). This permission will be used to its fullest extent.", size: 24 })]
        }),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.4 The NO ESCAPE Principle")] }),
        new Paragraph({
          spacing: { before: 200, after: 200 },
          children: [new TextRun({ text: "The user cannot escape accountability. Root access means the system can force-stop distracting apps. Hosts file modification means porn sites are blocked at DNS level. Background monitoring means the system sees everything. Wake lock means monitoring continues even when screen is off. There is no 'closing the app' to escape. There is no 'turning off notifications' to ignore. Accountability is enforced, not requested.", size: 24 })]
        }),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.5 The SELF-AWARE SYSTEM Principle")] }),
        new Paragraph({
          spacing: { before: 200, after: 200 },
          children: [new TextRun({ text: "The system evaluates its own effectiveness. When a rule fails to produce desired behaviour, the system generates a rewrite proposal with clear reasoning and expected benefit. User approval is required (YES/MODIFY/NO), but the system proactively identifies weaknesses and suggests improvements. Static systems decay. Self-aware systems evolve.", size: 24 })]
        }),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.6 The TECHNICAL-EXAM BALANCE Principle")] }),
        new Paragraph({
          spacing: { before: 200, after: 200 },
          children: [new TextRun({ text: "50% technical implementation, 50% exam impact mapping. Every technical module must have a documented: Subject affected, Habit affected, Marks impact estimate. A technically perfect feature with no exam impact is WASTE. A technically simple feature with high exam impact is GOLD. Implementation complexity does not equal value.", size: 24 })]
        }),

        // PART 3: ULTRA ADVANCED SYSTEM DESIGN
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("PART 3: ULTRA ADVANCED SYSTEM DESIGN")] }),
        
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.1 System Architecture Overview")] }),
        new Paragraph({
          spacing: { before: 200, after: 200 },
          children: [new TextRun({ text: "The redesigned system has four integrated layers that work together to ensure exam success. Each layer has a specific purpose and clear exam impact. No layer operates in isolation. All layers share data and coordinate actions. The system is a unified exam weapon, not a collection of independent features.", size: 24 })]
        }),

        // Architecture Layers Table
        new Table({
          columnWidths: [2340, 3510, 3510],
          margins: { top: 100, bottom: 100, left: 180, right: 180 },
          rows: [
            new TableRow({
              tableHeader: true,
              children: [
                new TableCell({ borders: cellBorders, shading: { fill: colors.tableBg, type: ShadingType.CLEAR }, verticalAlign: VerticalAlign.CENTER,
                  children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "LAYER", bold: true, size: 22 })] })] }),
                new TableCell({ borders: cellBorders, shading: { fill: colors.tableBg, type: ShadingType.CLEAR }, verticalAlign: VerticalAlign.CENTER,
                  children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "PURPOSE", bold: true, size: 22 })] })] }),
                new TableCell({ borders: cellBorders, shading: { fill: colors.tableBg, type: ShadingType.CLEAR }, verticalAlign: VerticalAlign.CENTER,
                  children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "EXAM IMPACT", bold: true, size: 22 })] })] })
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "BEHAVIOUR DOMINATION", bold: true, size: 22, color: colors.danger })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "24/7 monitoring, distraction blocking, pattern detection", size: 22 })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Prevents self-sabotage, ensures study hours", size: 22 })] })] })
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "ADAPTIVE STUDY", bold: true, size: 22, color: colors.warning })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "IRT-based difficulty adjustment, weakness targeting", size: 22 })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Maximizes learning efficiency per hour", size: 22 })] })] })
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "PSYCHOLOGICAL CONTROL", bold: true, size: 22, color: colors.success })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Loss aversion, variable rewards, social pressure", size: 22 })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Maintains motivation, prevents burnout", size: 22 })] })] })
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "VOICE ENFORCER", bold: true, size: 22, color: colors.primary })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Always-on voice layer, discipline enforcement", size: 22 })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Reduces friction, ensures routine compliance", size: 22 })] })] })
              ]
            })
          ]
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 100, after: 300 },
          children: [new TextRun({ text: "Table 2: System Architecture Layers", size: 20, color: colors.secondary, italics: true })]
        }),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.2 LAYER 1: BEHAVIOUR DOMINATION SYSTEM")] }),
        
        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("3.2.1 What Gets Monitored")] }),
        new Paragraph({
          spacing: { before: 200, after: 200 },
          children: [new TextRun({ text: "The system monitors every aspect of user behaviour that correlates with exam performance. This is not surveillance for surveillance's sake—every monitored metric has a documented impact on study effectiveness or indicates self-sabotage patterns.", size: 24 })]
        }),

        // Monitoring Metrics Table
        new Table({
          columnWidths: [2808, 2808, 3744],
          margins: { top: 100, bottom: 100, left: 180, right: 180 },
          rows: [
            new TableRow({
              tableHeader: true,
              children: [
                new TableCell({ borders: cellBorders, shading: { fill: colors.tableBg, type: ShadingType.CLEAR }, verticalAlign: VerticalAlign.CENTER,
                  children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "METRIC", bold: true, size: 22 })] })] }),
                new TableCell({ borders: cellBorders, shading: { fill: colors.tableBg, type: ShadingType.CLEAR }, verticalAlign: VerticalAlign.CENTER,
                  children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "COLLECTION METHOD", bold: true, size: 22 })] })] }),
                new TableCell({ borders: cellBorders, shading: { fill: colors.tableBg, type: ShadingType.CLEAR }, verticalAlign: VerticalAlign.CENTER,
                  children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "EXAM IMPACT", bold: true, size: 22 })] })] })
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "App Usage Time", size: 22 })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "dumpsys usagestats via root", size: 22 })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Direct: Time on distracting apps = less study time", size: 22 })] })] })
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Foreground App", size: 22 })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "dumpsys activity top (1s poll)", size: 22 })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Real-time distraction detection", size: 22 })] })] })
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Screen Unlocks", size: 22 })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "dumpsys power | grep 'mWakefulness'", size: 22 })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Focus fragmentation indicator", size: 22 })] })] })
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Screen On Duration", size: 22 })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "dumpsys display | grep 'mScreenState'", size: 22 })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Active usage time measurement", size: 22 })] })] })
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Porn Access Attempts", size: 22 })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "DNS queries via hosts file", size: 22 })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Cognitive dullness correlation", size: 22 })] })] })
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Instagram Usage", size: 22 })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Package name detection", size: 22 })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Dopamine crash + next-day impact", size: 22 })] })] })
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Sleep Time Detection", size: 22 })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Screen off patterns + time", size: 22 })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Sleep disruption = next-day performance", size: 22 })] })] })
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Study Session Duration", size: 22 })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "JARVIS session timestamps", size: 22 })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Actual study time vs claimed", size: 22 })] })] })
              ]
            })
          ]
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 100, after: 300 },
          children: [new TextRun({ text: "Table 3: Behaviour Monitoring Metrics", size: 20, color: colors.secondary, italics: true })]
        }),

        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("3.2.2 Distraction Blocking Implementation")] }),
        new Paragraph({
          spacing: { before: 200, after: 200 },
          children: [new TextRun({ text: "Porn blocking uses hosts file modification at DNS level. This is more reliable than app-level blocking because it works for all browsers and apps. The hosts file maps porn domains to 127.0.0.1, making them unreachable. A comprehensive list of 50,000+ porn domains will be used. This block is PERMANENT and cannot be bypassed without root access removal.", size: 24 })]
        }),
        new Paragraph({
          spacing: { before: 200, after: 200 },
          children: [new TextRun({ text: "Instagram blocking uses force-stop commands during study hours. The app is not uninstalled (which would cause resistance) but is repeatedly killed if opened during designated study time. This creates friction without permanent removal. The user can still use Instagram during designated break times.", size: 24 })]
        }),
        new Paragraph({
          spacing: { before: 200, after: 200 },
          children: [new TextRun({ text: "General distraction apps (89 apps identified) are categorized by severity. High-severity apps (TikTok, YouTube Shorts, games) are blocked during all study hours. Medium-severity apps (WhatsApp, Telegram) are allowed during breaks but monitored for excessive usage. Low-severity apps (news, shopping) are logged but not blocked.", size: 24 })]
        }),

        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("3.2.3 Pattern Detection Engine")] }),
        new Paragraph({
          spacing: { before: 200, after: 200 },
          children: [new TextRun({ text: "The system doesn't just log behaviour—it detects patterns that indicate self-sabotage. The pattern detection engine uses statistical analysis to identify deviations from productive routines. When a pattern is detected, the system initiates intervention protocols.", size: 24 })]
        }),

        // Pattern Detection Table
        new Table({
          columnWidths: [3120, 3120, 3120],
          margins: { top: 100, bottom: 100, left: 180, right: 180 },
          rows: [
            new TableRow({
              tableHeader: true,
              children: [
                new TableCell({ borders: cellBorders, shading: { fill: colors.tableBg, type: ShadingType.CLEAR }, verticalAlign: VerticalAlign.CENTER,
                  children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "PATTERN", bold: true, size: 22 })] })] }),
                new TableCell({ borders: cellBorders, shading: { fill: colors.tableBg, type: ShadingType.CLEAR }, verticalAlign: VerticalAlign.CENTER,
                  children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "DETECTION METHOD", bold: true, size: 22 })] })] }),
                new TableCell({ borders: cellBorders, shading: { fill: colors.tableBg, type: ShadingType.CLEAR }, verticalAlign: VerticalAlign.CENTER,
                  children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "INTERVENTION", bold: true, size: 22 })] })] })
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Study Avoidance", size: 22 })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Sequential app switches during study hours", size: 22 })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Voice confrontation + forced study mode", size: 22 })] })] })
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Late Night Dopamine", size: 22 })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Screen activity after 11 PM on distracting apps", size: 22 })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Device lock + morning confrontation", size: 22 })] })] })
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Burnout Precursor", size: 22 })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Declining session times + increasing breaks", size: 22 })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "20% target reduction + rest day suggestion", size: 22 })] })] })
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Weakness Avoidance", size: 22 })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Topic selection patterns over 7 days", size: 22 })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Forced weakness-targeted questions", size: 22 })] })] })
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Inconsistency Pattern", size: 22 })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Variance in daily study hours > 30%", size: 22 })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Streak threat + loss aversion trigger", size: 22 })] })] })
              ]
            })
          ]
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 100, after: 300 },
          children: [new TextRun({ text: "Table 4: Pattern Detection and Intervention Protocols", size: 20, color: colors.secondary, italics: true })]
        }),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.3 LAYER 2: ADAPTIVE STUDY ENGINE")] }),
        
        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("3.3.1 IRT-Based Difficulty Adjustment")] }),
        new Paragraph({
          spacing: { before: 200, after: 200 },
          children: [new TextRun({ text: "The existing IRT implementation (3PL model with Fisher Information) is retained. The system tracks user's theta (ability) for each subject separately. Questions are selected based on maximum information criterion—optimal difficulty is slightly above current ability. This ensures the user is always challenged but not overwhelmed.", size: 24 })]
        }),
        new Paragraph({
          spacing: { before: 200, after: 200 },
          children: [new TextRun({ text: "EXAM IMPACT: ", bold: true, size: 24, color: colors.success }), new TextRun({ text: "Direct. Maths carries 20 marks (highest weightage) and is user's weakest subject. IRT ensures every question is at optimal difficulty, maximizing learning per question. No time wasted on too-easy or too-hard questions.", size: 24 })]
        }),

        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("3.3.2 Weakness Hunting System")] }),
        new Paragraph({
          spacing: { before: 200, after: 200 },
          children: [new TextRun({ text: "The system actively hunts weaknesses rather than letting the user avoid them. Topic mastery data is analyzed to identify avoided topics. When avoidance is detected, the system forces questions from that topic with increasing frequency until mastery improves. This counteracts the natural tendency to practice strengths and avoid weaknesses.", size: 24 })]
        }),
        new Paragraph({
          spacing: { before: 200, after: 200 },
          children: [new TextRun({ text: "EXAM IMPACT: ", bold: true, size: 24, color: colors.success }), new TextRun({ text: "Direct. User's fear is 'Right effort, wrong strategy.' Weakness hunting ensures effort is directed where it's needed most. Exam questions don't avoid weak topics—the system ensures neither does the user.", size: 24 })]
        }),

        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("3.3.3 75-Day Personalized Plan")] }),
        new Paragraph({
          spacing: { before: 200, after: 200 },
          children: [new TextRun({ text: "The plan is rebuilt from scratch based on user's specific situation: Biology stream student attempting MPC exam. Foundation phase starts from 10th basics, not 12th. The plan accounts for the fundamental knowledge gap in Maths and Physics.", size: 24 })]
        }),

        // 75-Day Plan Table
        new Table({
          columnWidths: [1872, 2808, 2340, 2340],
          margins: { top: 100, bottom: 100, left: 180, right: 180 },
          rows: [
            new TableRow({
              tableHeader: true,
              children: [
                new TableCell({ borders: cellBorders, shading: { fill: colors.tableBg, type: ShadingType.CLEAR }, verticalAlign: VerticalAlign.CENTER,
                  children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "PHASE", bold: true, size: 22 })] })] }),
                new TableCell({ borders: cellBorders, shading: { fill: colors.tableBg, type: ShadingType.CLEAR }, verticalAlign: VerticalAlign.CENTER,
                  children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "DAYS", bold: true, size: 22 })] })] }),
                new TableCell({ borders: cellBorders, shading: { fill: colors.tableBg, type: ShadingType.CLEAR }, verticalAlign: VerticalAlign.CENTER,
                  children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "FOCUS", bold: true, size: 22 })] })] }),
                new TableCell({ borders: cellBorders, shading: { fill: colors.tableBg, type: ShadingType.CLEAR }, verticalAlign: VerticalAlign.CENTER,
                  children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "TARGET", bold: true, size: 22 })] })] })
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "FOUNDATION RUSH", bold: true, size: 22, color: colors.danger })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Day 1-25", size: 22 })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "10th basics (Maths/Physics)", size: 22 })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Build foundation from zero", size: 22 })] })] })
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "INTENSIVE PRACTICE", bold: true, size: 22, color: colors.warning })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Day 26-50", size: 22 })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "12th topics + Weakness targeting", size: 22 })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Close all knowledge gaps", size: 22 })] })] })
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "MOCK MARATHON", bold: true, size: 22, color: colors.success })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Day 51-70", size: 22 })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Full mock tests + Interview prep", size: 22 })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Exam simulation + speed", size: 22 })] })] })
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "FINAL REVISION", bold: true, size: 22, color: colors.primary })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Day 71-75", size: 22 })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Formula sheets + Quick revision", size: 22 })] })] }),
                new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Peak performance ready", size: 22 })] })] })
              ]
            })
          ]
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 100, after: 300 },
          children: [new TextRun({ text: "Table 5: 75-Day Personalized Study Plan", size: 20, color: colors.secondary, italics: true })]
        }),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.4 LAYER 3: PSYCHOLOGICAL CONTROL SYSTEM")] }),
        
        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("3.4.1 Loss Aversion Implementation")] }),
        new Paragraph({
          spacing: { before: 200, after: 200 },
          children: [new TextRun({ text: "Research proves losses feel 2x more painful than equivalent gains. The system exploits this. Streaks are prominently displayed, and breaking a streak triggers a prominent LOSS notification. XP is framed as something to lose, not something to gain. Daily targets are presented as minimum requirements to avoid losing progress, not goals to achieve.", size: 24 })]
        }),
        new Paragraph({
          spacing: { before: 200, after: 200 },
          children: [new TextRun({ text: "The system also implements 'streak threats'—warnings before streaks are broken. These are more effective than streak rewards because the pain of anticipated loss motivates action. The user will work harder to avoid losing a 20-day streak than to gain an achievement.", size: 24 })]
        }),

        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("3.4.2 Variable Reward System")] }),
        new Paragraph({
          spacing: { before: 200, after: 200 },
          children: [new TextRun({ text: "Dopamine optimization through unpredictable rewards. Every completed session has a chance at bonus rewards. Mystery boxes appear randomly. This creates anticipation and makes study sessions feel less monotonous. The reward structure mirrors slot machines—the most addictive design pattern known—applied to study behaviour.", size: 24 })]
        }),

        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("3.4.3 Burnout Prevention Protocol")] }),
        new Paragraph({
          spacing: { before: 200, after: 200 },
          children: [new TextRun({ text: "The user has a history of burnout. The system actively prevents this. When burnout precursors are detected (declining session times, increased app switching, shortened attention spans), the system automatically: Reduces daily targets by 20%, Suggests a rest day, Removes guilt messaging, Shifts focus to easier topics temporarily. Burnout prevention is prioritized over short-term progress.", size: 24 })]
        }),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.5 LAYER 4: VOICE ENFORCER SYSTEM")] }),
        
        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("3.5.1 Always-On Voice Layer")] }),
        new Paragraph({
          spacing: { before: 200, after: 200 },
          children: [new TextRun({ text: "The voice layer is not a voice assistant—it is a discipline enforcer. It replaces alarms with spoken messages. It checks routine completion at each step. It can be invoked anytime by speaking. It proactively speaks when intervention is needed. The voice layer removes friction from routine compliance and adds friction to routine avoidance.", size: 24 })]
        }),

        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("3.5.2 Routine Enforcement Flow")] }),
        new Paragraph({
          spacing: { before: 200, after: 200 },
          children: [new TextRun({ text: "Morning (6:00 AM): Voice alarm wakes user. System checks: Did you wake up? Brush teeth? Eat breakfast? Each step requires confirmation. Failure to confirm triggers escalation. Evening: Study session reminders. Bedtime: Sleep preparation prompts. The voice layer creates accountability without requiring screen interaction.", size: 24 })]
        }),

        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("3.5.3 Intervention Voice Messages")] }),
        new Paragraph({
          spacing: { before: 200, after: 200 },
          children: [new TextRun({ text: "The voice layer speaks proactively when intervention is needed. Examples: 'Tum abhi jhooth bol rahe ho' when claimed behaviour doesn't match monitored behaviour. 'Tum padhai se bhaag rahe ho' when study avoidance pattern detected. 'Phone band karo, abhi padhai shuru karo' when distraction detected during study hours. These messages are direct, uncomfortable, and impossible to ignore.", size: 24 })]
        }),

        // PART 4: IMPLEMENTATION ROADMAP
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("PART 4: IMPLEMENTATION ROADMAP - 80 SEQUENTIAL TASKS")] }),
        
        new Paragraph({
          spacing: { before: 200, after: 200 },
          children: [new TextRun({ text: "The following tasks must be completed in sequence. No parallel execution. Each task must be 100% complete, verified, tested, and documented before moving to the next. Every script has a rollback plan. Every decision has a written reason.", size: 24 })]
        }),

        // Phase 1 Tasks
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("PHASE 1: FOUNDATION (Tasks 1-15)")] }),
        new Paragraph({ numbering: { reference: "numbered-list-1", level: 0 }, children: [new TextRun({ text: "Document all system requirements with exam impact mapping", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-1", level: 0 }, children: [new TextRun({ text: "Create project structure for Termux + Python environment", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-1", level: 0 }, children: [new TextRun({ text: "Write Termux setup script with all dependencies", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-1", level: 0 }, children: [new TextRun({ text: "Create rollback script for Termux setup", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-1", level: 0 }, children: [new TextRun({ text: "Implement root access verification function", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-1", level: 0 }, children: [new TextRun({ text: "Test root access on device (or document emulator alternative)", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-1", level: 0 }, children: [new TextRun({ text: "Set up SQLite database with complete schema", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-1", level: 0 }, children: [new TextRun({ text: "Create database migration and rollback scripts", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-1", level: 0 }, children: [new TextRun({ text: "Install and configure llama.cpp for Android", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-1", level: 0 }, children: [new TextRun({ text: "Download and integrate DeepSeek-R1:1.5B quantized model", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-1", level: 0 }, children: [new TextRun({ text: "Test LLM response time and quality benchmarks", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-1", level: 0 }, children: [new TextRun({ text: "Implement response caching system in SQLite", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-1", level: 0 }, children: [new TextRun({ text: "Create TUI framework using Textual (Python)", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-1", level: 0 }, children: [new TextRun({ text: "Build basic navigation and screen structure", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-1", level: 0 }, children: [new TextRun({ text: "Document Phase 1 completion with verification checklist", size: 24 })] }),

        // Phase 2 Tasks
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("PHASE 2: BEHAVIOUR DOMINATION (Tasks 16-30)")] }),
        new Paragraph({ numbering: { reference: "numbered-list-2", level: 0 }, children: [new TextRun({ text: "Implement foreground app detection via dumpsys", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-2", level: 0 }, children: [new TextRun({ text: "Create 1-second polling loop for app monitoring", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-2", level: 0 }, children: [new TextRun({ text: "Implement screen state monitoring (on/off/unlock)", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-2", level: 0 }, children: [new TextRun({ text: "Create app usage time tracking system", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-2", level: 0 }, children: [new TextRun({ text: "Implement sleep time inference from screen patterns", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-2", level: 0 }, children: [new TextRun({ text: "Create wake lock acquisition script (termux-wake-lock)", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-2", level: 0 }, children: [new TextRun({ text: "Build background monitoring service with auto-restart", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-2", level: 0 }, children: [new TextRun({ text: "Implement force-stop command execution (su -c 'am force-stop')", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-2", level: 0 }, children: [new TextRun({ text: "Test force-stop on Instagram and YouTube apps", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-2", level: 0 }, children: [new TextRun({ text: "Create hosts file with comprehensive porn domain list", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-2", level: 0 }, children: [new TextRun({ text: "Implement hosts file deployment script (su -c mount -o remount,rw)", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-2", level: 0 }, children: [new TextRun({ text: "Test porn site blocking in all browsers", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-2", level: 0 }, children: [new TextRun({ text: "Create rollback script for hosts file modification", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-2", level: 0 }, children: [new TextRun({ text: "Implement distraction logging to database", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-2", level: 0 }, children: [new TextRun({ text: "Document Phase 2 completion with verification checklist", size: 24 })] }),

        // Phase 3 Tasks
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("PHASE 3: PATTERN DETECTION (Tasks 31-42)")] }),
        new Paragraph({ numbering: { reference: "numbered-list-3", level: 0 }, children: [new TextRun({ text: "Implement study avoidance pattern detection algorithm", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-3", level: 0 }, children: [new TextRun({ text: "Create late-night dopamine pattern detector", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-3", level: 0 }, children: [new TextRun({ text: "Implement burnout precursor detection", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-3", level: 0 }, children: [new TextRun({ text: "Create weakness avoidance detection from topic selection", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-3", level: 0 }, children: [new TextRun({ text: "Implement inconsistency pattern detection (variance analysis)", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-3", level: 0 }, children: [new TextRun({ text: "Create pattern severity scoring system", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-3", level: 0 }, children: [new TextRun({ text: "Implement intervention trigger conditions", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-3", level: 0 }, children: [new TextRun({ text: "Create intervention action execution system", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-3", level: 0 }, children: [new TextRun({ text: "Build daily behaviour summary generator", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-3", level: 0 }, children: [new TextRun({ text: "Implement weekly pattern analysis report", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-3", level: 0 }, children: [new TextRun({ text: "Create pattern-to-exam-impact correlation display", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-3", level: 0 }, children: [new TextRun({ text: "Document Phase 3 completion with verification checklist", size: 24 })] }),

        // Phase 4 Tasks
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("PHASE 4: ADAPTIVE STUDY ENGINE (Tasks 43-55)")] }),
        new Paragraph({ numbering: { reference: "numbered-list-4", level: 0 }, children: [new TextRun({ text: "Port existing IRT algorithm to Python (from TypeScript)", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-4", level: 0 }, children: [new TextRun({ text: "Implement per-subject theta tracking", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-4", level: 0 }, children: [new TextRun({ text: "Create question selection by maximum information", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-4", level: 0 }, children: [new TextRun({ text: "Implement SM-2 spaced repetition algorithm", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-4", level: 0 }, children: [new TextRun({ text: "Create topic mastery tracking system", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-4", level: 0 }, children: [new TextRun({ text: "Implement weakness hunting algorithm", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-4", level: 0 }, children: [new TextRun({ text: "Create question bank for Maths (10th + 12th basics)", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-4", level: 0 }, children: [new TextRun({ text: "Create question bank for Physics (10th + 12th basics)", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-4", level: 0 }, children: [new TextRun({ text: "Create question bank for Chemistry", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-4", level: 0 }, children: [new TextRun({ text: "Create question bank for English", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-4", level: 0 }, children: [new TextRun({ text: "Implement LLM-based question generation with caching", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-4", level: 0 }, children: [new TextRun({ text: "Create pre-generation script for overnight question banks", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-4", level: 0 }, children: [new TextRun({ text: "Document Phase 4 completion with verification checklist", size: 24 })] }),

        // Phase 5 Tasks
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("PHASE 5: PSYCHOLOGICAL CONTROL (Tasks 56-65)")] }),
        new Paragraph({ numbering: { reference: "numbered-list-5", level: 0 }, children: [new TextRun({ text: "Port psychological engine to Python", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-5", level: 0 }, children: [new TextRun({ text: "Implement loss aversion messaging system", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-5", level: 0 }, children: [new TextRun({ text: "Create variable reward generator", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-5", level: 0 }, children: [new TextRun({ text: "Implement streak tracking and threat system", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-5", level: 0 }, children: [new TextRun({ text: "Create XP and level progression system", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-5", level: 0 }, children: [new TextRun({ text: "Implement burnout prevention protocol", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-5", level: 0 }, children: [new TextRun({ text: "Create daily target adjustment based on performance", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-5", level: 0 }, children: [new TextRun({ text: "Implement achievement system with meaningful unlocks", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-5", level: 0 }, children: [new TextRun({ text: "Create leaderboard simulation (self-competition)", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-5", level: 0 }, children: [new TextRun({ text: "Document Phase 5 completion with verification checklist", size: 24 })] }),

        // Phase 6 Tasks
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("PHASE 6: VOICE ENFORCER (Tasks 66-72)")] }),
        new Paragraph({ numbering: { reference: "numbered-list-6", level: 0 }, children: [new TextRun({ text: "Implement TTS (Text-to-Speech) integration for Termux", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-6", level: 0 }, children: [new TextRun({ text: "Implement STT (Speech-to-Text) for voice commands", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-6", level: 0 }, children: [new TextRun({ text: "Create routine enforcement flow with voice prompts", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-6", level: 0 }, children: [new TextRun({ text: "Implement intervention voice messages (direct, harsh)", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-6", level: 0 }, children: [new TextRun({ text: "Create always-on voice listener service", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-6", level: 0 }, children: [new TextRun({ text: "Implement voice-based study session control", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-6", level: 0 }, children: [new TextRun({ text: "Document Phase 6 completion with verification checklist", size: 24 })] }),

        // Phase 7 Tasks
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("PHASE 7: 75-DAY PLAN & MOCK TESTS (Tasks 73-80)")] }),
        new Paragraph({ numbering: { reference: "numbered-list-7", level: 0 }, children: [new TextRun({ text: "Generate Foundation Rush content (Day 1-25)", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-7", level: 0 }, children: [new TextRun({ text: "Generate Intensive Practice content (Day 26-50)", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-7", level: 0 }, children: [new TextRun({ text: "Create mock test system with exam pattern simulation", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-7", level: 0 }, children: [new TextRun({ text: "Implement interview preparation module", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-7", level: 0 }, children: [new TextRun({ text: "Create daily plan generator with energy-based scheduling", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-7", level: 0 }, children: [new TextRun({ text: "Implement progress tracking dashboard in TUI", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-7", level: 0 }, children: [new TextRun({ text: "Create final verification and testing protocol", size: 24 })] }),
        new Paragraph({ numbering: { reference: "numbered-list-7", level: 0 }, children: [new TextRun({ text: "Document complete system with user guide", size: 24 })] }),

        // PART 5: ROLLBACK DOCUMENTATION
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("PART 5: ROLLBACK PLANS FOR CRITICAL OPERATIONS")] }),
        
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("5.1 Root Access Operations Rollback")] }),
        new Paragraph({
          spacing: { before: 200, after: 200 },
          children: [new TextRun({ text: "Every root operation has a documented rollback procedure. Hosts file modification: Original hosts file is backed up to /sdcard/jarvis_backup/hosts_original. Rollback script copies original back and flushes DNS cache. Force-stop operations: No persistent state change, rollbacks not needed. Wake lock: termux-wake-unlock command releases. Database operations: SQLite backup before every migration, rollback script available.", size: 24 })]
        }),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("5.2 System State Recovery")] }),
        new Paragraph({
          spacing: { before: 200, after: 200 },
          children: [new TextRun({ text: "Full system state is backed up daily to /sdcard/jarvis_backup/. This includes: Database file, User preferences, Theta scores per subject, Streak and XP data, Question bank status. Recovery script restores any previous day's state. Recovery time target: Under 2 minutes.", size: 24 })]
        }),

        // FINAL DECLARATION
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("FINAL DECLARATION")] }),
        new Paragraph({
          spacing: { before: 200, after: 200 },
          children: [new TextRun({ text: "This document represents the complete analysis of previous implementation flaws and the complete design for JARVIS 8.0 ULTRA. The system is designed with ONE PURPOSE: LOYOLA COLLEGE SEAT CONFIRMATION. Every feature has documented exam impact. Every decision has written reasoning. Every script has rollback plan. Implementation will proceed through 80 sequential tasks with 100% completion verification at each stage.", size: 24 })]
        }),
        new Paragraph({
          spacing: { before: 200, after: 200 },
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "MODE: RUTHLESS | GOAL: SEAT CONFIRMATION | PERMISSION: FULL MONITORING", bold: true, size: 24, color: colors.primary })]
        }),
        new Paragraph({
          spacing: { before: 100, after: 200 },
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "BUILD PHASE BEGINS NOW", bold: true, size: 28, color: colors.success })]
        })
      ]
    }
  ]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/home/z/my-project/download/JARVIS_ULTRA_DEEP_ANALYSIS_REPORT.docx", buffer);
  console.log("Document created: JARVIS_ULTRA_DEEP_ANALYSIS_REPORT.docx");
});
