#!/usr/bin/env node
/**
 * Code Review Evaluation Report Generator
 * 코드 완성도 평가 결과를 1장 PPTX로 생성
 * 
 * Usage:
 *   node generate_report.js \
 *     --title "프로젝트명" \
 *     --score 85 \
 *     --grades '{"logic":"A","completeness":"B","structure":"A","syntax":"A","efficiency":"B","naming":"B","consistency":"A"}' \
 *     --summary "핵심 평가 요약" \
 *     --output report.pptx
 */

const pptxgen = require("pptxgenjs");

// Parse command line arguments
function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    title: "Code Review Report",
    score: 0,
    grades: {},
    summary: "",
    output: "evaluation_report.pptx"
  };

  for (let i = 0; i < args.length; i += 2) {
    const key = args[i].replace("--", "");
    const value = args[i + 1];
    
    if (key === "grades") {
      options[key] = JSON.parse(value);
    } else if (key === "score") {
      options[key] = parseInt(value);
    } else {
      options[key] = value;
    }
  }

  return options;
}

// Get grade color
function getGradeColor(grade) {
  const colors = {
    A: "2E7D32", // Green
    B: "1976D2", // Blue
    C: "F57C00", // Orange
    D: "D32F2F"  // Red
  };
  return colors[grade] || "757575";
}

// Get overall grade from score
function getOverallGrade(score) {
  if (score >= 90) return "A";
  if (score >= 75) return "B";
  if (score >= 60) return "C";
  return "D";
}

// Create the presentation
function createReport(options) {
  const pres = new pptxgen();
  
  pres.layout = "LAYOUT_16x9";
  pres.title = options.title;
  pres.author = "Code Review Evaluator";

  const slide = pres.addSlide();
  
  // Color scheme
  const PRIMARY = "1E3A5F";      // Dark blue
  const SECONDARY = "F5F7FA";    // Light gray bg
  const ACCENT = "0D9488";       // Teal
  const TEXT_DARK = "1F2937";
  const TEXT_MUTED = "6B7280";

  // Background
  slide.background = { color: SECONDARY };

  // Header bar
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.9,
    fill: { color: PRIMARY }
  });

  // Title
  slide.addText(options.title, {
    x: 0.5, y: 0.2, w: 7, h: 0.5,
    fontSize: 24, fontFace: "Arial", bold: true,
    color: "FFFFFF"
  });

  // Date
  const today = new Date().toLocaleDateString("ko-KR");
  slide.addText(`평가일: ${today}`, {
    x: 7.5, y: 0.3, w: 2, h: 0.3,
    fontSize: 11, fontFace: "Arial",
    color: "CADCFC", align: "right"
  });

  // === Main Score Section (Left) ===
  const overallGrade = getOverallGrade(options.score);
  
  // Score circle background
  slide.addShape(pres.shapes.OVAL, {
    x: 0.7, y: 1.3, w: 2.2, h: 2.2,
    fill: { color: "FFFFFF" },
    line: { color: getGradeColor(overallGrade), width: 4 }
  });

  // Score number
  slide.addText(String(options.score), {
    x: 0.7, y: 1.7, w: 2.2, h: 1.0,
    fontSize: 48, fontFace: "Arial", bold: true,
    color: getGradeColor(overallGrade), align: "center"
  });

  // "/100" text
  slide.addText("/100", {
    x: 0.7, y: 2.6, w: 2.2, h: 0.4,
    fontSize: 14, fontFace: "Arial",
    color: TEXT_MUTED, align: "center"
  });

  // Overall grade label
  slide.addText(`종합 등급: ${overallGrade}`, {
    x: 0.5, y: 3.6, w: 2.6, h: 0.4,
    fontSize: 16, fontFace: "Arial", bold: true,
    color: TEXT_DARK, align: "center"
  });

  // Grade meaning
  const gradeMeanings = {
    A: "우수 - 프로덕션 준비 완료",
    B: "양호 - 소규모 개선 후 배포 가능",
    C: "보통 - 상당한 개선 필요",
    D: "미흡 - 대폭 수정 필요"
  };
  slide.addText(gradeMeanings[overallGrade], {
    x: 0.3, y: 4.0, w: 3.0, h: 0.3,
    fontSize: 10, fontFace: "Arial",
    color: TEXT_MUTED, align: "center"
  });

  // === Grades Table Section (Center) ===
  slide.addText("항목별 평가", {
    x: 3.5, y: 1.1, w: 3.5, h: 0.4,
    fontSize: 14, fontFace: "Arial", bold: true,
    color: TEXT_DARK
  });

  // Grade items
  const gradeItems = [
    { key: "logic", name: "로직 정확성", weight: "25%" },
    { key: "completeness", name: "완결성", weight: "25%" },
    { key: "structure", name: "구조적 연결성", weight: "15%" },
    { key: "syntax", name: "문법적 정확성", weight: "10%" },
    { key: "efficiency", name: "효율성", weight: "10%" },
    { key: "naming", name: "명명 규칙", weight: "10%" },
    { key: "consistency", name: "일관성", weight: "5%" }
  ];

  let yPos = 1.55;
  gradeItems.forEach((item) => {
    const grade = options.grades[item.key] || "-";
    const gradeColor = getGradeColor(grade);

    // Item row background
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 3.5, y: yPos, w: 3.3, h: 0.42,
      fill: { color: "FFFFFF" },
      line: { color: "E5E7EB", width: 0.5 }
    });

    // Item name
    slide.addText(`${item.name} (${item.weight})`, {
      x: 3.6, y: yPos + 0.08, w: 2.4, h: 0.28,
      fontSize: 10, fontFace: "Arial",
      color: TEXT_DARK
    });

    // Grade badge
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 6.35, y: yPos + 0.06, w: 0.35, h: 0.30,
      fill: { color: gradeColor }
    });
    slide.addText(grade, {
      x: 6.35, y: yPos + 0.06, w: 0.35, h: 0.30,
      fontSize: 11, fontFace: "Arial", bold: true,
      color: "FFFFFF", align: "center", valign: "middle"
    });

    yPos += 0.44;
  });

  // === Summary Section (Right) ===
  slide.addText("평가 요약", {
    x: 7.1, y: 1.1, w: 2.6, h: 0.4,
    fontSize: 14, fontFace: "Arial", bold: true,
    color: TEXT_DARK
  });

  // Summary box
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 7.1, y: 1.55, w: 2.6, h: 2.5,
    fill: { color: "FFFFFF" },
    line: { color: ACCENT, width: 2 }
  });

  slide.addText(options.summary || "평가 요약 내용이 없습니다.", {
    x: 7.25, y: 1.7, w: 2.3, h: 2.2,
    fontSize: 10, fontFace: "Arial",
    color: TEXT_DARK, valign: "top"
  });

  // === Footer ===
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 5.25, w: 10, h: 0.375,
    fill: { color: PRIMARY }
  });

  slide.addText("Generated by Code Review Evaluator Skill", {
    x: 0.5, y: 5.3, w: 9, h: 0.25,
    fontSize: 9, fontFace: "Arial",
    color: "CADCFC", align: "center"
  });

  // Save file
  pres.writeFile({ fileName: options.output })
    .then(() => {
      console.log(`✅ Report saved: ${options.output}`);
    })
    .catch((err) => {
      console.error(`❌ Error: ${err}`);
      process.exit(1);
    });
}

// Main
const options = parseArgs();
createReport(options);
