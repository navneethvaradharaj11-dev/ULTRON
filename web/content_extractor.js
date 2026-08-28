/**
 * ULTRON Content Extractor
 * Extracts structured elements, readable text, links, and forms from DOM context.
 */

class ULTRONContentExtractor {
    static extractPageStructure(documentObj) {
        if (!documentObj) {
            return { title: "", elements: [], text: "", links: [] };
        }

        const title = documentObj.title || "";
        const text = (documentObj.body ? documentObj.body.innerText : "").replace(/\s+/g, ' ').slice(0, 5000);

        const elements = [];
        const links = [];

        const interactiveNodes = documentObj.querySelectorAll ? 
            documentObj.querySelectorAll('button, input, select, a, textarea, form') : [];

        let index = 1;
        interactiveNodes.forEach((node) => {
            const tagName = node.tagName.toLowerCase();
            const type = node.type || tagName;
            const textContent = (node.innerText || node.value || "").trim();
            const id = node.id || `elem_${index++}`;

            if (tagName === 'a' && node.href) {
                links.append ? links.append({ text: textContent, url: node.href }) : links.push({ text: textContent, url: node.href });
            }

            elements.push({
                id: id,
                type: type,
                role: node.getAttribute('role') || tagName,
                text: textContent.slice(0, 100),
                label: node.getAttribute('aria-label') || node.placeholder || ""
            });
        });

        return {
            title: title,
            elements: elements.slice(0, 50),
            text: text,
            links: links.slice(0, 30)
        };
    }
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ULTRONContentExtractor };
}
