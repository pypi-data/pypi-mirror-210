"use strict";
(self["webpackChunkyjs_widgets"] = self["webpackChunkyjs_widgets"] || []).push([["lib_index_js"],{

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   IJupyterYWidgetManager: () => (/* reexport safe */ _notebookrenderer_types__WEBPACK_IMPORTED_MODULE_2__.IJupyterYWidgetManager),
/* harmony export */   JupyterYDoc: () => (/* reexport safe */ _model__WEBPACK_IMPORTED_MODULE_0__.JupyterYDoc),
/* harmony export */   JupyterYModel: () => (/* reexport safe */ _model__WEBPACK_IMPORTED_MODULE_0__.JupyterYModel),
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__),
/* harmony export */   notebookRenderer: () => (/* reexport safe */ _notebookrenderer__WEBPACK_IMPORTED_MODULE_1__.notebookRenderer),
/* harmony export */   yWidgetManager: () => (/* reexport safe */ _notebookrenderer__WEBPACK_IMPORTED_MODULE_1__.yWidgetManager)
/* harmony export */ });
/* harmony import */ var _model__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./model */ "./lib/model.js");
/* harmony import */ var _notebookrenderer__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./notebookrenderer */ "./lib/notebookrenderer/index.js");
/* harmony import */ var _notebookrenderer_types__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./notebookrenderer/types */ "./lib/notebookrenderer/types.js");





/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = ([_notebookrenderer__WEBPACK_IMPORTED_MODULE_1__.notebookRenderer, _notebookrenderer__WEBPACK_IMPORTED_MODULE_1__.yWidgetManager]);


/***/ }),

/***/ "./lib/model.js":
/*!**********************!*\
  !*** ./lib/model.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   JupyterYDoc: () => (/* binding */ JupyterYDoc),
/* harmony export */   JupyterYModel: () => (/* binding */ JupyterYModel)
/* harmony export */ });
/* harmony import */ var _lumino_coreutils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/coreutils */ "webpack/sharing/consume/default/@lumino/coreutils");
/* harmony import */ var _lumino_coreutils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_coreutils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @lumino/signaling */ "webpack/sharing/consume/default/@lumino/signaling");
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_lumino_signaling__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var yjs__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! yjs */ "webpack/sharing/consume/default/yjs");
/* harmony import */ var yjs__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(yjs__WEBPACK_IMPORTED_MODULE_2__);



class JupyterYModel {
    constructor(commMetadata) {
        this._isDisposed = false;
        this._disposed = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal(this);
        this._yModelName = commMetadata.ymodel_name;
        const ydoc = this.ydocFactory(commMetadata);
        this._sharedModel = new JupyterYDoc(commMetadata, ydoc);
    }
    get yModelName() {
        return this._yModelName;
    }
    get sharedModel() {
        return this._sharedModel;
    }
    get sharedAttrsChanged() {
        return this.sharedModel.attrsChanged;
    }
    get disposed() {
        return this._disposed;
    }
    get isDisposed() {
        return this._isDisposed;
    }
    ydocFactory(commMetadata) {
        return new yjs__WEBPACK_IMPORTED_MODULE_2__.Doc();
    }
    dispose() {
        if (this._isDisposed) {
            return;
        }
        this._isDisposed = true;
        this._sharedModel.dispose();
        this._disposed.emit();
        _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal.clearData(this);
    }
    addAttr(key, value) {
        this.sharedModel.setAttr(key, value);
    }
    removeAttr(key) {
        this.sharedModel.removeAttr(key);
    }
}
class JupyterYDoc {
    constructor(commMetadata, ydoc) {
        this._attrsObserver = (event) => {
            this._attrsChanged.emit(event.keys);
        };
        this._attrsChanged = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal(this);
        this._isDisposed = false;
        this._disposed = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal(this);
        this._commMetadata = commMetadata;
        this._ydoc = ydoc;
        if (commMetadata.create_ydoc) {
            this._attrs = this._ydoc.getMap('_attrs');
            this._attrs.observe(this._attrsObserver);
        }
    }
    get commMetadata() {
        return this._commMetadata;
    }
    get ydoc() {
        return this._ydoc;
    }
    get attrs() {
        return _lumino_coreutils__WEBPACK_IMPORTED_MODULE_0__.JSONExt.deepCopy(this._attrs.toJSON());
    }
    get attrsChanged() {
        return this._attrsChanged;
    }
    get disposed() {
        return this._disposed;
    }
    get isDisposed() {
        return this._isDisposed;
    }
    dispose() {
        if (this._isDisposed) {
            return;
        }
        this._attrs.unobserve(this._attrsObserver);
        this._disposed.emit();
        _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal.clearData(this);
        this._isDisposed = true;
    }
    getAttr(key) {
        return this._attrs.get(key);
    }
    setAttr(key, value) {
        this._attrs.set(key, value);
    }
    removeAttr(key) {
        if (this._attrs.has(key)) {
            this._attrs.delete(key);
        }
    }
}


/***/ }),

/***/ "./lib/notebookrenderer/index.js":
/*!***************************************!*\
  !*** ./lib/notebookrenderer/index.js ***!
  \***************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   notebookRenderer: () => (/* binding */ notebookRenderer),
/* harmony export */   yWidgetManager: () => (/* binding */ yWidgetManager)
/* harmony export */ });
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/notebook */ "webpack/sharing/consume/default/@jupyterlab/notebook");
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_rendermime__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/rendermime */ "webpack/sharing/consume/default/@jupyterlab/rendermime");
/* harmony import */ var _jupyterlab_rendermime__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_rendermime__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _model__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./model */ "./lib/notebookrenderer/model.js");
/* harmony import */ var _types__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./types */ "./lib/notebookrenderer/types.js");
/* harmony import */ var _view__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./view */ "./lib/notebookrenderer/view.js");
/* harmony import */ var _widgetManager__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./widgetManager */ "./lib/notebookrenderer/widgetManager.js");






const MIME_TYPE = 'application/vnd.jupyter.ywidget-view+json';
const notebookRenderer = {
    id: 'jupyterywidget:notebookRenderer',
    autoStart: true,
    requires: [_jupyterlab_rendermime__WEBPACK_IMPORTED_MODULE_1__.IRenderMimeRegistry, _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__.INotebookTracker, _types__WEBPACK_IMPORTED_MODULE_2__.IJupyterYWidgetManager],
    activate: (app, rendermime, nbTracker, wmManager) => {
        const rendererFactory = {
            safe: true,
            mimeTypes: [MIME_TYPE],
            createRenderer: options => {
                var _a, _b, _c;
                const kernelId = (_c = (_b = (_a = nbTracker.currentWidget) === null || _a === void 0 ? void 0 : _a.sessionContext.session) === null || _b === void 0 ? void 0 : _b.kernel) === null || _c === void 0 ? void 0 : _c.id;
                const mimeType = options.mimeType;
                const modelFactory = new _model__WEBPACK_IMPORTED_MODULE_3__.NotebookRendererModel({
                    kernelId,
                    widgetManager: wmManager
                });
                return new _view__WEBPACK_IMPORTED_MODULE_4__.JupyterYWidget({ mimeType, modelFactory });
            }
        };
        rendermime.addFactory(rendererFactory, -100);
    }
};
const yWidgetManager = {
    id: 'yjs-widgets:yWidgetManagerPlugin',
    autoStart: true,
    requires: [_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__.INotebookTracker],
    provides: _types__WEBPACK_IMPORTED_MODULE_2__.IJupyterYWidgetManager,
    activate: (app, tracker) => {
        const registry = new _widgetManager__WEBPACK_IMPORTED_MODULE_5__.JupyterYWidgetManager();
        const onKernelChanged = (_, changedArgs) => {
            const { newValue, oldValue } = changedArgs;
            if (newValue) {
                registry.unregisterKernel(oldValue === null || oldValue === void 0 ? void 0 : oldValue.id);
                registry.registerKernel(newValue);
                newValue.disposed.connect(() => {
                    registry.unregisterKernel(newValue.id);
                });
            }
        };
        tracker.widgetAdded.connect(async (_, notebook) => {
            notebook.sessionContext.kernelChanged.connect(onKernelChanged);
            notebook.disposed.connect(() => {
                notebook.sessionContext.kernelChanged.disconnect(onKernelChanged);
            });
        });
        return registry;
    }
};


/***/ }),

/***/ "./lib/notebookrenderer/model.js":
/*!***************************************!*\
  !*** ./lib/notebookrenderer/model.js ***!
  \***************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   NotebookRendererModel: () => (/* binding */ NotebookRendererModel)
/* harmony export */ });
class NotebookRendererModel {
    constructor(options) {
        this._isDisposed = false;
        this._widgetManager = options.widgetManager;
        this._kernelId = options.kernelId;
    }
    get isDisposed() {
        return this._isDisposed;
    }
    dispose() {
        if (this._isDisposed) {
            return;
        }
        this._isDisposed = true;
    }
    getYModel(commId) {
        if (this._kernelId) {
            return this._widgetManager.getWidgetModel(this._kernelId, commId);
        }
    }
    createYWidget(commId, node) {
        if (this._kernelId) {
            const yModel = this._widgetManager.getWidgetModel(this._kernelId, commId);
            if (yModel) {
                const widgetFactory = this._widgetManager.getWidgetFactory(yModel.yModelName);
                new widgetFactory(yModel, node);
            }
        }
    }
}


/***/ }),

/***/ "./lib/notebookrenderer/types.js":
/*!***************************************!*\
  !*** ./lib/notebookrenderer/types.js ***!
  \***************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   IJupyterYWidgetManager: () => (/* binding */ IJupyterYWidgetManager)
/* harmony export */ });
/* harmony import */ var _lumino_coreutils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/coreutils */ "webpack/sharing/consume/default/@lumino/coreutils");
/* harmony import */ var _lumino_coreutils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_coreutils__WEBPACK_IMPORTED_MODULE_0__);

const IJupyterYWidgetManager = new _lumino_coreutils__WEBPACK_IMPORTED_MODULE_0__.Token('yjs-widgets:IJupyterYWidgetManager', 'A manager of Yjs-based Jupyter widgets.');


/***/ }),

/***/ "./lib/notebookrenderer/view.js":
/*!**************************************!*\
  !*** ./lib/notebookrenderer/view.js ***!
  \**************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   CLASS_NAME: () => (/* binding */ CLASS_NAME),
/* harmony export */   JupyterYWidget: () => (/* binding */ JupyterYWidget)
/* harmony export */ });
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_0__);

const CLASS_NAME = 'mimerenderer-jupyterywidget';
class JupyterYWidget extends _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__.Widget {
    /**
     * Construct a new output widget.
     */
    constructor(options) {
        super();
        this._modelFactory = options.modelFactory;
        this._mimeType = options.mimeType;
        this.addClass(CLASS_NAME);
    }
    dispose() {
        var _a;
        if (this.isDisposed) {
            return;
        }
        (_a = this._yModel) === null || _a === void 0 ? void 0 : _a.dispose();
        super.dispose();
    }
    async renderModel(mimeModel) {
        const modelId = mimeModel.data[this._mimeType]['model_id'];
        this._yModel = this._modelFactory.getYModel(modelId);
        if (!this._yModel) {
            return;
        }
        this._modelFactory.createYWidget(modelId, this.node);
    }
}


/***/ }),

/***/ "./lib/notebookrenderer/widgetManager.js":
/*!***********************************************!*\
  !*** ./lib/notebookrenderer/widgetManager.js ***!
  \***********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   JupyterYWidgetManager: () => (/* binding */ JupyterYWidgetManager),
/* harmony export */   WidgetModelRegistry: () => (/* binding */ WidgetModelRegistry)
/* harmony export */ });
/* harmony import */ var _yCommProvider__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./yCommProvider */ "./lib/notebookrenderer/yCommProvider.js");

class JupyterYWidgetManager {
    constructor() {
        this._registry = new Map();
        this._yModelFactories = new Map();
        this._yWidgetFactories = new Map();
    }
    registerKernel(kernel) {
        const yModelFactories = this._yModelFactories;
        const wm = new WidgetModelRegistry({ kernel, yModelFactories });
        this._registry.set(kernel.id, wm);
    }
    unregisterKernel(kernelId) {
        if (kernelId) {
            this._registry.delete(kernelId);
        }
    }
    registerWidget(name, yModelFactory, yWidgetFactory) {
        this._yModelFactories.set(name, yModelFactory);
        this._yWidgetFactories.set(name, yWidgetFactory);
    }
    getWidgetModel(kernelId, commId) {
        var _a;
        return (_a = this._registry.get(kernelId)) === null || _a === void 0 ? void 0 : _a.getModel(commId);
    }
    getWidgetFactory(modelName) {
        return this._yWidgetFactories.get(modelName);
    }
}
class WidgetModelRegistry {
    constructor(options) {
        /**
         * Handle when a comm is opened.
         */
        this._handle_comm_open = async (comm, msg) => {
            const yModelFactory = this._yModelFactories.get(msg.metadata.ymodel_name);
            const yModel = new yModelFactory(msg.metadata);
            new _yCommProvider__WEBPACK_IMPORTED_MODULE_0__.YCommProvider({
                comm,
                ydoc: yModel.sharedModel.ydoc
            });
            this._yModels.set(comm.commId, yModel);
        };
        this._yModels = new Map();
        const { kernel, yModelFactories } = options;
        this._yModelFactories = yModelFactories;
        kernel.registerCommTarget('ywidget', this._handle_comm_open);
    }
    getModel(id) {
        return this._yModels.get(id);
    }
}


/***/ }),

/***/ "./lib/notebookrenderer/yCommProvider.js":
/*!***********************************************!*\
  !*** ./lib/notebookrenderer/yCommProvider.js ***!
  \***********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   YCommProvider: () => (/* binding */ YCommProvider),
/* harmony export */   YMessageType: () => (/* binding */ YMessageType)
/* harmony export */ });
/* harmony import */ var lib0_decoding__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! lib0/decoding */ "./node_modules/lib0/decoding.js");
/* harmony import */ var lib0_encoding__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! lib0/encoding */ "./node_modules/lib0/encoding.js");
/* harmony import */ var y_protocols_sync__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! y-protocols/sync */ "./node_modules/y-protocols/sync.js");



var YMessageType;
(function (YMessageType) {
    YMessageType[YMessageType["SYNC"] = 0] = "SYNC";
    YMessageType[YMessageType["AWARENESS"] = 1] = "AWARENESS";
})(YMessageType || (YMessageType = {}));
class YCommProvider {
    constructor(options) {
        this._onMsg = (msg) => {
            if (msg.buffers) {
                const buffer = msg.buffers[0];
                const buffer_uint8 = new Uint8Array(ArrayBuffer.isView(buffer) ? buffer.buffer : buffer);
                const encoder = Private.readMessage(this, buffer_uint8, true);
                if (lib0_encoding__WEBPACK_IMPORTED_MODULE_1__.length(encoder) > 1) {
                    this._sendOverComm(lib0_encoding__WEBPACK_IMPORTED_MODULE_1__.toUint8Array(encoder));
                }
            }
        };
        this._updateHandler = (update, origin) => {
            const encoder = lib0_encoding__WEBPACK_IMPORTED_MODULE_1__.createEncoder();
            lib0_encoding__WEBPACK_IMPORTED_MODULE_1__.writeVarUint(encoder, YMessageType.SYNC);
            y_protocols_sync__WEBPACK_IMPORTED_MODULE_0__.writeUpdate(encoder, update);
            this._sendOverComm(lib0_encoding__WEBPACK_IMPORTED_MODULE_1__.toUint8Array(encoder));
        };
        this._isDisposed = false;
        this._comm = options.comm;
        this._ydoc = options.ydoc;
        this._ydoc.on('update', this._updateHandler);
        this._connect();
    }
    get doc() {
        return this._ydoc;
    }
    get synced() {
        return this._synced;
    }
    set synced(state) {
        if (this._synced !== state) {
            this._synced = state;
        }
    }
    get isDisposed() {
        return this._isDisposed;
    }
    dispose() {
        if (this._isDisposed) {
            return;
        }
        this._comm.close();
        this._isDisposed = true;
    }
    _connect() {
        this._sync();
        this._comm.onMsg = this._onMsg;
    }
    _sync() {
        const encoder = lib0_encoding__WEBPACK_IMPORTED_MODULE_1__.createEncoder();
        lib0_encoding__WEBPACK_IMPORTED_MODULE_1__.writeVarUint(encoder, YMessageType.SYNC);
        y_protocols_sync__WEBPACK_IMPORTED_MODULE_0__.writeSyncStep1(encoder, this._ydoc);
        this._sendOverComm(lib0_encoding__WEBPACK_IMPORTED_MODULE_1__.toUint8Array(encoder));
    }
    _sendOverComm(bufferArray) {
        this._comm.send({}, undefined, [bufferArray.buffer]);
    }
}
var Private;
(function (Private) {
    function syncMessageHandler(encoder, decoder, provider, emitSynced) {
        lib0_encoding__WEBPACK_IMPORTED_MODULE_1__.writeVarUint(encoder, YMessageType.SYNC);
        const syncMessageType = y_protocols_sync__WEBPACK_IMPORTED_MODULE_0__.readSyncMessage(decoder, encoder, provider.doc, provider);
        if (emitSynced &&
            syncMessageType === y_protocols_sync__WEBPACK_IMPORTED_MODULE_0__.messageYjsSyncStep2 &&
            !provider.synced) {
            y_protocols_sync__WEBPACK_IMPORTED_MODULE_0__.writeSyncStep2(encoder, provider.doc);
            provider.synced = true;
        }
    }
    Private.syncMessageHandler = syncMessageHandler;
    function readMessage(provider, buf, emitSynced) {
        const decoder = lib0_decoding__WEBPACK_IMPORTED_MODULE_2__.createDecoder(buf);
        const encoder = lib0_encoding__WEBPACK_IMPORTED_MODULE_1__.createEncoder();
        const messageType = lib0_decoding__WEBPACK_IMPORTED_MODULE_2__.readVarUint(decoder);
        if (messageType === YMessageType.SYNC) {
            syncMessageHandler(encoder, decoder, provider, emitSynced);
        }
        else {
            console.error('Unable to compute message');
        }
        return encoder;
    }
    Private.readMessage = readMessage;
})(Private || (Private = {}));


/***/ })

}]);
//# sourceMappingURL=lib_index_js.155e0d17339dc6c3d2e5.js.map