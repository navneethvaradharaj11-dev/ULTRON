/**
 * ULTRON Browser Agent Client
 * Client script managing browser session communication and DOM event bridge.
 */

const { ULTRONPageBridge } = typeof require !== 'undefined' ? require('./page_bridge') : { ULTRONPageBridge };
const { ULTRONContentExtractor } = typeof require !== 'undefined' ? require('./content_extractor') : { ULTRONContentExtractor };

class ULTRONBrowserAgentClient {
    constructor(sessionId, userId) {
        this.sessionId = sessionId;
        this.userId = userId;
        this.bridge = new ULTRONPageBridge();
    }

    async handleInstruction(actionName, params) {
        const bridgeRes = await this.bridge.dispatchCommand(actionName, params);
        if (!bridgeRes.success) {
            return bridgeRes;
        }

        if (actionName === 'read_page') {
            const structure = ULTRONContentExtractor.extractPageStructure(typeof document !== 'undefined' ? document : null);
            return { success: true, page: structure };
        }

        return {
            success: true,
            action: actionName,
            params: params,
            sessionId: this.sessionId
        };
    }
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ULTRONBrowserAgentClient };
}
