// ULTRON Browser Agent Abstraction
class BrowserAgent {
    inspectDOM() {
        return {
            title: document.title,
            url: window.location.href,
            elementsCount: document.getElementsByTagName('*').length
        };
    }

    captureViewport() {
        return {
            width: window.innerWidth,
            height: window.innerHeight
        };
    }
}

window.browserAgent = new BrowserAgent();
