const EXCEL_XML_HEADER = '<?xml version="1.0"?><?mso-application progid="Excel.Sheet"?>';

const escapeXml = (value) =>
  String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");

const inferCellType = (value) => {
  if (typeof value === "number" && Number.isFinite(value)) {
    return "Number";
  }

  if (typeof value === "boolean") {
    return "String";
  }

  return "String";
};

const serializeCell = (value) => {
  const type = inferCellType(value);
  const text = type === "Number" ? String(value) : escapeXml(value);
  return `<Cell><Data ss:Type="${type}">${text}</Data></Cell>`;
};

const serializeRow = (values) => `<Row>${values.map(serializeCell).join("")}</Row>`;

const buildWorksheetXml = (sheet) => {
  const rows = [];

  if (Array.isArray(sheet.headers) && sheet.headers.length > 0) {
    rows.push(serializeRow(sheet.headers));
  }

  (sheet.rows || []).forEach((row) => {
    rows.push(serializeRow(row));
  });

  return `
    <Worksheet ss:Name="${escapeXml(sheet.name || "Sheet1")}">
      <Table>
        ${rows.join("")}
      </Table>
    </Worksheet>
  `;
};

export const downloadBlob = (fileName, blob) => {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = fileName;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
};

export const exportWorkbookXml = ({ fileName, sheets }) => {
  const workbookXml = `
    ${EXCEL_XML_HEADER}
    <Workbook
      xmlns="urn:schemas-microsoft-com:office:spreadsheet"
      xmlns:o="urn:schemas-microsoft-com:office:office"
      xmlns:x="urn:schemas-microsoft-com:office:excel"
      xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet"
      xmlns:html="http://www.w3.org/TR/REC-html40"
    >
      ${sheets.map(buildWorksheetXml).join("")}
    </Workbook>
  `.trim();

  const blob = new Blob([workbookXml], {
    type: "application/vnd.ms-excel;charset=utf-8;",
  });

  downloadBlob(fileName, blob);
};

const escapeHtml = (value) =>
  String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");

const renderPrintSection = (section) => {
  if (section.type === "table") {
    const headers = section.headers || [];
    const rows = section.rows || [];
    return `
      <section class="print-section">
        <h2>${escapeHtml(section.title || "")}</h2>
        <table>
          <thead>
            <tr>${headers.map((header) => `<th>${escapeHtml(header)}</th>`).join("")}</tr>
          </thead>
          <tbody>
            ${rows
              .map(
                (row) =>
                  `<tr>${row.map((cell) => `<td>${escapeHtml(cell)}</td>`).join("")}</tr>`
              )
              .join("")}
          </tbody>
        </table>
      </section>
    `;
  }

  if (section.type === "list") {
    return `
      <section class="print-section">
        <h2>${escapeHtml(section.title || "")}</h2>
        <ul>
          ${(section.items || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
        </ul>
      </section>
    `;
  }

  return `
    <section class="print-section">
      <h2>${escapeHtml(section.title || "")}</h2>
      ${(section.lines || []).map((line) => `<p>${escapeHtml(line)}</p>`).join("")}
    </section>
  `;
};

export const openPrintDocument = ({ title, subtitle, logoDataUrl, sections }) => {
  const printWindow = window.open("", "_blank", "noopener,noreferrer,width=1080,height=820");
  if (!printWindow) {
    throw new Error("Unable to open print window");
  }

  const body = `
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8" />
        <title>${escapeHtml(title)}</title>
        <style>
          body {
            font-family: Arial, sans-serif;
            color: #0f172a;
            margin: 32px;
            line-height: 1.45;
          }
          .print-header {
            display: flex;
            align-items: center;
            gap: 16px;
            border-bottom: 2px solid #cbd5e1;
            padding-bottom: 16px;
            margin-bottom: 24px;
          }
          .print-header img {
            max-height: 44px;
          }
          .print-header h1 {
            margin: 0;
            font-size: 24px;
          }
          .print-header p {
            margin: 4px 0 0;
            color: #475569;
          }
          .print-section {
            margin-bottom: 24px;
            page-break-inside: avoid;
          }
          .print-section h2 {
            margin: 0 0 12px;
            font-size: 16px;
            color: #0f172a;
          }
          table {
            width: 100%;
            border-collapse: collapse;
          }
          th, td {
            border: 1px solid #cbd5e1;
            padding: 8px 10px;
            text-align: left;
            vertical-align: top;
          }
          th {
            background: #f8fafc;
          }
          ul {
            margin: 0;
            padding-left: 18px;
          }
          p {
            margin: 0 0 8px;
          }
          @media print {
            body {
              margin: 18px;
            }
          }
        </style>
      </head>
      <body>
        <header class="print-header">
          ${logoDataUrl ? `<img src="${logoDataUrl}" alt="Logo" />` : ""}
          <div>
            <h1>${escapeHtml(title)}</h1>
            ${subtitle ? `<p>${escapeHtml(subtitle)}</p>` : ""}
          </div>
        </header>
        ${(sections || []).map(renderPrintSection).join("")}
      </body>
    </html>
  `;

  printWindow.document.open();
  printWindow.document.write(body);
  printWindow.document.close();
  printWindow.focus();
  setTimeout(() => {
    printWindow.print();
  }, 200);
};
