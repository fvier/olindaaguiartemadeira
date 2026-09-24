(function (global) {
    'use strict';

    function safeFileName(value) {
        return String(value || 'relatorio')
            .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
            .replace(/[^a-zA-Z0-9._-]+/g, '_');
    }

    function downloadBlob(blob, fileName) {
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = safeFileName(fileName);
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.setTimeout(() => URL.revokeObjectURL(url), 1000);
    }

    function exportCsv(rows, fileName) {
        const escape = value => `"${String(value ?? '').replace(/"/g, '""')}"`;
        const content = '\uFEFF' + rows.map(row => row.map(escape).join(';')).join('\r\n');
        downloadBlob(new Blob([content], {type: 'text/csv;charset=utf-8'}), fileName);
    }

    function exportXlsx(rows, sheetName, fileName) {
        if (!global.XLSX) throw new Error('O componente de Excel não foi carregado. Recarregue a página e tente novamente.');
        const worksheet = global.XLSX.utils.aoa_to_sheet(rows);
        const workbook = global.XLSX.utils.book_new();
        global.XLSX.utils.book_append_sheet(workbook, worksheet, String(sheetName || 'Relatorio').slice(0, 31));
        global.XLSX.writeFile(workbook, safeFileName(fileName), {compression: true});
    }

    function exportPdf(options) {
        const JsPdf = global.jspdf && global.jspdf.jsPDF;
        if (!JsPdf) throw new Error('O componente de PDF não foi carregado. Recarregue a página e tente novamente.');
        const doc = new JsPdf({orientation: 'landscape', unit: 'mm', format: 'a4', compress: true});
        if (typeof doc.autoTable !== 'function') throw new Error('O componente de tabelas PDF não foi carregado.');

        const accent = options.accent || [37, 99, 235];
        const emittedAt = new Date().toLocaleString('pt-BR');
        const drawHeader = () => {
            doc.setFillColor(...accent);
            doc.rect(0, 0, 297, 19, 'F');
            doc.setTextColor(255, 255, 255);
            doc.setFont('helvetica', 'bold');
            doc.setFontSize(14);
            doc.text('GPS PARAIBA', 12, 8);
            doc.setFontSize(10);
            doc.text(options.title, 12, 14);
            doc.setFont('helvetica', 'normal');
            doc.setFontSize(8);
            doc.text(`Solicitante: ${options.requester}  |  Emissao: ${emittedAt}`, 285, 8, {align: 'right'});
            doc.text(options.summary || '', 285, 14, {align: 'right'});
        };

        doc.autoTable({
            head: [options.columns],
            body: options.rows,
            startY: 24,
            margin: {top: 24, right: 8, bottom: 13, left: 8},
            theme: 'grid',
            styles: {font: 'helvetica', fontSize: 7.5, cellPadding: 2, overflow: 'linebreak', valign: 'middle'},
            headStyles: {fillColor: accent, textColor: 255, fontStyle: 'bold'},
            alternateRowStyles: {fillColor: [248, 250, 252]},
            rowPageBreak: 'avoid',
            showHead: 'everyPage',
            didDrawPage: data => {
                drawHeader();
                const pageNumber = doc.internal.getNumberOfPages();
                doc.setTextColor(100, 116, 139);
                doc.setFontSize(8);
                doc.text(`Pagina ${pageNumber}`, 285, 204, {align: 'right'});
            }
        });
        doc.save(safeFileName(options.fileName));
    }

    global.GpsReportExport = {downloadBlob, exportCsv, exportXlsx, exportPdf, safeFileName};
})(window);
