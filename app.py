import streamlit as st
from pypdf import PdfReader
from docx import Document
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)
from reportlab.lib.units import mm
from io import BytesIO

from plagiarism_detector import SemanticPlagiarismDetector


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="SemantiCheck AI",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# DETECTOR
# ============================================================

@st.cache_resource
def load_detector():
    return SemanticPlagiarismDetector()


# ============================================================
# FILE READING
# ============================================================

def read_pdf(uploaded_file):

    reader = PdfReader(uploaded_file)

    pages = []

    for page in reader.pages:

        text = page.extract_text()

        if text:
            pages.append(text)

    return "\n".join(pages)


def read_docx(uploaded_file):

    document = Document(uploaded_file)

    paragraphs = []

    for paragraph in document.paragraphs:

        if paragraph.text.strip():
            paragraphs.append(paragraph.text)

    return "\n".join(paragraphs)


def read_txt(uploaded_file):

    return uploaded_file.read().decode(
        "utf-8",
        errors="ignore"
    )


def extract_text(uploaded_file):

    if uploaded_file is None:
        return ""

    filename = uploaded_file.name.lower()

    try:

        if filename.endswith(".pdf"):
            return read_pdf(uploaded_file)

        if filename.endswith(".docx"):
            return read_docx(uploaded_file)

        if filename.endswith(".txt"):
            return read_txt(uploaded_file)

        return ""

    except Exception as error:

        st.error(
            "Unable to read the file: " + str(error)
        )

        return ""


# ============================================================
# PDF REPORT GENERATOR
# ============================================================

def create_pdf_report(
    similarity,
    risk,
    threshold,
    source_sections,
    submitted_sections,
    matches
):

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=24,
        leading=28,
        alignment=TA_CENTER,
        spaceAfter=8,
    )

    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=11,
        leading=16,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=20,
    )

    heading_style = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        fontSize=16,
        leading=20,
        spaceBefore=12,
        spaceAfter=10,
        textColor=colors.HexColor("#111827"),
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontSize=9,
        leading=14,
        textColor=colors.HexColor("#334155"),
    )

    small_style = ParagraphStyle(
        "Small",
        parent=styles["BodyText"],
        fontSize=8,
        leading=12,
        textColor=colors.HexColor("#64748b"),
    )

    story = []

    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "🔎 SemantiCheck AI",
            title_style
        )
    )

    story.append(
        Paragraph(
            "Semantic Plagiarism Detection Report",
            subtitle_style
        )
    )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Analysis Summary",
            heading_style
        )
    )

    summary_data = [
        ["Metric", "Result"],
        [
            "Overall Semantic Similarity",
            f"{similarity:.2f}%"
        ],
        [
            "Risk Level",
            risk
        ],
        [
            "Similarity Threshold",
            f"{threshold * 100:.0f}%"
        ],
        [
            "Original Sections",
            str(source_sections)
        ],
        [
            "Submitted Sections",
            str(submitted_sections)
        ],
        [
            "Matching Sections",
            str(len(matches))
        ],
    ]

    summary_table = Table(
        summary_data,
        colWidths=[
            90 * mm,
            75 * mm
        ]
    )

    summary_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#111827")
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),
                (
                    "FONTNAME",
                    (0, 1),
                    (0, -1),
                    "Helvetica-Bold"
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#e5e7eb")
                ),
                (
                    "BACKGROUND",
                    (0, 1),
                    (-1, -1),
                    colors.HexColor("#f8fafc")
                ),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [
                        colors.white,
                        colors.HexColor("#f8fafc")
                    ]
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                ),
            ]
        )
    )

    story.append(summary_table)

    story.append(Spacer(1, 15))

    # --------------------------------------------------------
    # RISK
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Risk Assessment",
            heading_style
        )
    )

    risk_color = "#15803d"

    if risk == "HIGH":
        risk_color = "#be123c"

    elif risk == "MEDIUM":
        risk_color = "#b45309"

    risk_table = Table(
        [
            [
                Paragraph(
                    f"<b>{risk} RISK</b>",
                    ParagraphStyle(
                        "RiskText",
                        parent=body_style,
                        fontSize=14,
                        alignment=TA_CENTER,
                        textColor=colors.HexColor(
                            risk_color
                        ),
                    )
                )
            ]
        ],
        colWidths=[165 * mm]
    )

    risk_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.HexColor("#f8fafc")
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    1,
                    colors.HexColor(risk_color)
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    12
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    12
                ),
            ]
        )
    )

    story.append(risk_table)

    # --------------------------------------------------------
    # MATCHES
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Matching Sections",
            heading_style
        )
    )

    if not matches:

        story.append(
            Paragraph(
                "No significant semantic matches were detected.",
                body_style
            )
        )

    else:

        for number, match in enumerate(
            matches,
            start=1
        ):

            score = (
                match["similarity"] * 100
            )

            story.append(
                Paragraph(
                    f"<b>Match {number} — "
                    f"{score:.2f}% similarity</b>",
                    body_style
                )
            )

            story.append(
                Spacer(1, 5)
            )

            submitted_text = (
                match["submitted_section"]
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )

            original_text = (
                match["source_section"]
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )

            match_data = [
                [
                    Paragraph(
                        "<b>Submitted Section</b>",
                        body_style
                    ),
                    Paragraph(
                        "<b>Original Section</b>",
                        body_style
                    ),
                ],
                [
                    Paragraph(
                        submitted_text,
                        small_style
                    ),
                    Paragraph(
                        original_text,
                        small_style
                    ),
                ],
            ]

            match_table = Table(
                match_data,
                colWidths=[
                    80 * mm,
                    80 * mm
                ]
            )

            match_table.setStyle(
                TableStyle(
                    [
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, 0),
                            colors.HexColor("#eef2ff")
                        ),
                        (
                            "GRID",
                            (0, 0),
                            (-1, -1),
                            0.5,
                            colors.HexColor("#e5e7eb")
                        ),
                        (
                            "VALIGN",
                            (0, 0),
                            (-1, -1),
                            "TOP"
                        ),
                        (
                            "TOPPADDING",
                            (0, 0),
                            (-1, -1),
                            8
                        ),
                        (
                            "BOTTOMPADDING",
                            (0, 0),
                            (-1, -1),
                            8
                        ),
                    ]
                )
            )

            story.append(match_table)
            story.append(Spacer(1, 12))

    # --------------------------------------------------------
    # METHODOLOGY
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Methodology",
            heading_style
        )
    )

    methodology = (
        "SemantiCheck AI uses the Sentence Transformer "
        "model <b>all-MiniLM-L6-v2</b> to convert document "
        "sections into semantic embeddings. Cosine similarity "
        "is then used to compare the meaning of submitted "
        "sections against the original document."
    )

    story.append(
        Paragraph(
            methodology,
            body_style
        )
    )

    story.append(Spacer(1, 8))

    limitation = (
        "<b>Important:</b> The similarity score is an "
        "AI-based heuristic. It should not be treated as "
        "a definitive academic or legal determination "
        "of plagiarism."
    )

    story.append(
        Paragraph(
            limitation,
            body_style
        )
    )

    # --------------------------------------------------------
    # FOOTER
    # --------------------------------------------------------

    story.append(Spacer(1, 25))

    story.append(
        Paragraph(
            "Generated by SemantiCheck AI",
            subtitle_style
        )
    )

    document.build(story)

    buffer.seek(0)

    return buffer.getvalue()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🔎 SemantiCheck AI")

    st.caption(
        "Semantic Plagiarism Detection"
    )

    st.divider()

    st.subheader("⚙️ Detection Settings")

    threshold = st.slider(
        "Similarity threshold",
        min_value=0.50,
        max_value=0.95,
        value=0.70,
        step=0.05
    )

    st.write(
        f"Current threshold: {threshold * 100:.0f}%"
    )

    st.divider()

    st.subheader("🧠 AI Pipeline")

    st.write("📄 Document extraction")
    st.write("🧹 Text preprocessing")
    st.write("🧠 Semantic embeddings")
    st.write("🔗 Cosine similarity")
    st.write("🔍 Match detection")
    st.write("📊 Report generation")

    st.divider()

    st.subheader("🤖 Model")

    st.info(
        "all-MiniLM-L6-v2\n\n"
        "Method: Cosine Similarity"
    )


# ============================================================
# HEADER
# ============================================================

st.title("🔎 SemantiCheck AI")

st.subheader(
    "Intelligent Semantic Plagiarism Detection"
)

st.caption(
    "Detect similar meaning even when the wording "
    "has been changed through paraphrasing."
)


# ============================================================
# DOCUMENT INPUT
# ============================================================

st.header("📄 Compare Documents")

st.write(
    "Upload PDF, DOCX or TXT documents, "
    "or paste text directly."
)


left_column, right_column = st.columns(
    2,
    gap="large"
)


# ============================================================
# ORIGINAL DOCUMENT
# ============================================================

with left_column:

    st.subheader("📚 Original Document")

    st.caption(
        "Reference or source document"
    )

    original_file = st.file_uploader(
        "Upload original document",
        type=["pdf", "docx", "txt"],
        key="original_file"
    )

    if original_file:

        original_text = extract_text(
            original_file
        )

        st.success(
            f"✓ {original_file.name} loaded"
        )

        with st.expander(
            "👁️ Preview original document"
        ):

            st.text(
                original_text[:5000]
            )

    else:

        original_text = st.text_area(
            "Or paste original text",
            height=250,
            placeholder=(
                "Paste the original document here..."
            ),
            key="original_text"
        )


# ============================================================
# SUBMITTED DOCUMENT
# ============================================================

with right_column:

    st.subheader("📝 Submitted Document")

    st.caption(
        "Document that will be analyzed"
    )

    submitted_file = st.file_uploader(
        "Upload submitted document",
        type=["pdf", "docx", "txt"],
        key="submitted_file"
    )

    if submitted_file:

        submitted_text = extract_text(
            submitted_file
        )

        st.success(
            f"✓ {submitted_file.name} loaded"
        )

        with st.expander(
            "👁️ Preview submitted document"
        ):

            st.text(
                submitted_text[:5000]
            )

    else:

        submitted_text = st.text_area(
            "Or paste submitted text",
            height=250,
            placeholder=(
                "Paste the submitted document here..."
            ),
            key="submitted_text"
        )


# ============================================================
# ANALYZE BUTTON
# ============================================================

st.write("")

analyze = st.button(
    "🔍 Analyze Semantic Similarity",
    type="primary",
    use_container_width=True
)


# ============================================================
# ANALYSIS
# ============================================================

if analyze:

    if not original_text.strip():

        st.warning(
            "⚠️ Please provide the original document."
        )

        st.stop()


    if not submitted_text.strip():

        st.warning(
            "⚠️ Please provide the submitted document."
        )

        st.stop()


    detector = load_detector()


    with st.spinner(
        "🤖 AI is analyzing the documents..."
    ):

        result = detector.generate_report(
            original_text,
            submitted_text,
            threshold
        )


    similarity = result[
        "overall_similarity"
    ]

    matches = result[
        "matches"
    ]

    source_sections = result[
        "source_sections"
    ]

    submitted_sections = result[
        "submitted_sections"
    ]


    # ========================================================
    # RESULTS
    # ========================================================

    st.divider()

    st.header("📊 Analysis Results")

    st.success(
        "✓ Semantic comparison completed."
    )


    # ========================================================
    # METRICS
    # ========================================================

    metric1, metric2, metric3, metric4 = st.columns(4)


    with metric1:

        st.metric(
            "Semantic Similarity",
            f"{similarity:.1f}%"
        )


    with metric2:

        st.metric(
            "Matching Sections",
            len(matches)
        )


    with metric3:

        st.metric(
            "Original Sections",
            source_sections
        )


    with metric4:

        st.metric(
            "Submitted Sections",
            submitted_sections
        )


    # ========================================================
    # SCORE
    # ========================================================

    st.subheader(
        "🎯 Overall Similarity"
    )

    st.progress(
        min(max(similarity / 100, 0), 1)
    )

    st.write(
        f"**Similarity Score: {similarity:.1f}%**"
    )


    # ========================================================
    # RISK
    # ========================================================

    st.subheader(
        "🚦 Risk Assessment"
    )


    if similarity >= 70:

        risk = "HIGH"

        st.error(
            "🔴 HIGH RISK — Strong semantic similarity detected."
        )

    elif similarity >= 40:

        risk = "MEDIUM"

        st.warning(
            "🟡 MEDIUM RISK — Moderate semantic similarity detected."
        )

    else:

        risk = "LOW"

        st.success(
            "🟢 LOW RISK — Limited semantic similarity detected."
        )


    # ========================================================
    # MATCHING SECTIONS
    # ========================================================

    st.divider()

    st.header(
        "🔗 Matching Sections"
    )

    st.caption(
        "Sections that exceeded the selected similarity threshold."
    )


    if not matches:

        st.success(
            "✓ No significant semantic matches detected."
        )

    else:

        for number, match in enumerate(
            matches,
            start=1
        ):

            score = (
                match["similarity"] * 100
            )

            st.subheader(
                f"Match {number} — {score:.1f}% similarity"
            )


            submitted_column, original_column = st.columns(
                2,
                gap="large"
            )


            with submitted_column:

                st.markdown(
                    "**📝 Submitted Section**"
                )

                st.info(
                    match["submitted_section"]
                )


            with original_column:

                st.markdown(
                    "**📚 Original Section**"
                )

                st.info(
                    match["source_section"]
                )


    # ========================================================
    # AI PIPELINE
    # ========================================================

    st.divider()

    st.header(
        "🧠 How the AI Works"
    )


    pipeline1, pipeline2, pipeline3, pipeline4 = st.columns(4)


    with pipeline1:

        st.subheader("📄 Extract")

        st.caption(
            "Read text from PDF, DOCX or TXT."
        )


    with pipeline2:

        st.subheader("🧠 Embed")

        st.caption(
            "Convert text into semantic vectors."
        )


    with pipeline3:

        st.subheader("🔗 Compare")

        st.caption(
            "Calculate cosine similarity."
        )


    with pipeline4:

        st.subheader("📊 Report")

        st.caption(
            "Generate explainable results."
        )


    # ========================================================
    # PDF REPORT
    # ========================================================

    st.divider()

    st.header(
        "📄 Professional PDF Report"
    )

    st.caption(
        "Download a formatted PDF containing "
        "the complete analysis."
    )


    pdf_data = create_pdf_report(
        similarity=similarity,
        risk=risk,
        threshold=threshold,
        source_sections=source_sections,
        submitted_sections=submitted_sections,
        matches=matches
    )


    st.download_button(
        label="📥 Download Professional PDF Report",
        data=pdf_data,
        file_name="SemantiCheck_AI_Report.pdf",
        mime="application/pdf",
        use_container_width=True
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🔎 SemantiCheck AI • Semantic Plagiarism Detection Agent"
)