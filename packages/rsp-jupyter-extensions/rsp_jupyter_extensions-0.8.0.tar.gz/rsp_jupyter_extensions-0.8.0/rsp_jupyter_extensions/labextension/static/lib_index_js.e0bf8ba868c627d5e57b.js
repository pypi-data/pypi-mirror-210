"use strict";
(self["webpackChunkrsp_jupyter_extensions"] = self["webpackChunkrsp_jupyter_extensions"] || []).push([["lib_index_js"],{

/***/ "./lib/DisplayLabVersion.js":
/*!**********************************!*\
  !*** ./lib/DisplayLabVersion.js ***!
  \**********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "DisplayLabVersion": () => (/* binding */ DisplayLabVersion),
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_statusbar__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/statusbar */ "webpack/sharing/consume/default/@jupyterlab/statusbar");
/* harmony import */ var _jupyterlab_statusbar__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_statusbar__WEBPACK_IMPORTED_MODULE_2__);



/**
 * A pure function for rendering the displayversion information.
 *
 * @param props: the props for rendering the component.
 *
 * @returns a tsx component for displaying version information.
 */
function DisplayLabVersionComponent(props) {
    return (react__WEBPACK_IMPORTED_MODULE_0__.createElement(_jupyterlab_statusbar__WEBPACK_IMPORTED_MODULE_2__.TextItem, { source: `${(props.source)}`, title: `${(props.title)}` }));
}
class DisplayLabVersion extends _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.VDomRenderer {
    /**
     * Create a new DisplayLabVersion widget.
     */
    constructor(props) {
        super(new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.VDomModel());
        this.props = props;
    }
    /**
     * Render the display Lab version widget.
     */
    render() {
        if (!this.props) {
            return null;
        }
        return (react__WEBPACK_IMPORTED_MODULE_0__.createElement(DisplayLabVersionComponent, { source: this.props.source, title: this.props.title }));
    }
    /**
     * Dispose of the item.
     */
    dispose() {
        super.dispose();
    }
}
;
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (DisplayLabVersion);


/***/ }),

/***/ "./lib/displayversion.js":
/*!*******************************!*\
  !*** ./lib/displayversion.js ***!
  \*******************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "activateRSPDisplayVersionExtension": () => (/* binding */ activateRSPDisplayVersionExtension),
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/coreutils */ "webpack/sharing/consume/default/@jupyterlab/coreutils");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/services */ "webpack/sharing/consume/default/@jupyterlab/services");
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_statusbar__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/statusbar */ "webpack/sharing/consume/default/@jupyterlab/statusbar");
/* harmony import */ var _jupyterlab_statusbar__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_statusbar__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _DisplayLabVersion__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./DisplayLabVersion */ "./lib/DisplayLabVersion.js");
/* harmony import */ var _tokens__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./tokens */ "./lib/tokens.js");
// Copyright (c) LSST DM/SQuaRE
// Distributed under the terms of the MIT License.





/**
 * Activate the extension.
 */
function activateRSPDisplayVersionExtension(app, statusBar) {
    console.log('RSP DisplayVersion extension: loading...');
    let svcManager = app.serviceManager;
    let endpoint = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.PageConfig.getBaseUrl() + "rubin/environment";
    let init = {
        method: "GET"
    };
    let settings = svcManager.serverSettings;
    apiRequest(endpoint, init, settings).then((res) => {
        let image_description = (res.IMAGE_DESCRIPTION || "");
        let image_digest = res.IMAGE_DIGEST;
        let image_spec = res.JUPYTER_IMAGE_SPEC;
        let instance_url = new URL(res.EXTERNAL_INSTANCE_URL || "");
        let hostname = " " + instance_url.hostname;
        let digest_str = "";
        if (image_digest) {
            digest_str = " [" + image_digest.substring(0, 8) + "...]";
        }
        let imagename = "";
        if (image_spec) {
            let imagearr = image_spec.split("/");
            imagename = " (" + imagearr[imagearr.length - 1] + ")";
        }
        let label = image_description + digest_str + imagename + hostname;
        const displayVersionWidget = new _DisplayLabVersion__WEBPACK_IMPORTED_MODULE_3__["default"]({
            source: label,
            title: image_description
        });
        statusBar.registerStatusItem(_tokens__WEBPACK_IMPORTED_MODULE_4__.DISPLAYVERSION_ID, {
            item: displayVersionWidget,
            align: "left",
            rank: 80,
            isActive: () => true
        });
    });
    function apiRequest(url, init, settings) {
        /**
        * Make a request to our endpoint to get the version
        *
        * @param url - the path for the displayversion extension
        *
        * @param init - The GET for the extension
        *
        * @param settings - the settings for the current notebook server
        *
        * @returns a Promise resolved with the JSON response
        */
        // Fake out URL check in makeRequest
        return _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeRequest(url, init, settings).then(response => {
            if (response.status !== 200) {
                return response.json().then(data => {
                    throw new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.ResponseError(response, data.message);
                });
            }
            return response.json();
        });
    }
    console.log('RSP DisplayVersion extension: ... loaded');
}
;
/**
 * Initialization data for the RSPdisplayversionextension extension.
 */
const rspDisplayVersionExtension = {
    activate: activateRSPDisplayVersionExtension,
    id: _tokens__WEBPACK_IMPORTED_MODULE_4__.DISPLAYVERSION_ID,
    requires: [
        _jupyterlab_statusbar__WEBPACK_IMPORTED_MODULE_2__.IStatusBar,
    ],
    autoStart: false,
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (rspDisplayVersionExtension);


/***/ }),

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_statusbar__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/statusbar */ "webpack/sharing/consume/default/@jupyterlab/statusbar");
/* harmony import */ var _jupyterlab_statusbar__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_statusbar__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/mainmenu */ "webpack/sharing/consume/default/@jupyterlab/mainmenu");
/* harmony import */ var _jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/docmanager */ "webpack/sharing/consume/default/@jupyterlab/docmanager");
/* harmony import */ var _jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _displayversion__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./displayversion */ "./lib/displayversion.js");
/* harmony import */ var _query__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./query */ "./lib/query.js");
/* harmony import */ var _savequit__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./savequit */ "./lib/savequit.js");
/* harmony import */ var _tokens__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ./tokens */ "./lib/tokens.js");







function activateRSPExtension(app, mainMenu, docManager, statusBar) {
    console.log('rsp-lab-extension: loading...');
    console.log('...activating displayversion extension...');
    (0,_displayversion__WEBPACK_IMPORTED_MODULE_3__.activateRSPDisplayVersionExtension)(app, statusBar);
    console.log('...activated...');
    console.log('...activating savequit extension...');
    (0,_savequit__WEBPACK_IMPORTED_MODULE_4__.activateRSPSavequitExtension)(app, mainMenu, docManager);
    console.log('...activated...');
    console.log('...activating query extension...');
    (0,_query__WEBPACK_IMPORTED_MODULE_5__.activateRSPQueryExtension)(app, mainMenu, docManager);
    console.log('...activated...');
    console.log('...loaded rsp-lab-extension.');
}
/**
 * Initialization data for the rspExtensions.
 */
const rspExtension = {
    activate: activateRSPExtension,
    id: _tokens__WEBPACK_IMPORTED_MODULE_6__.PLUGIN_ID,
    requires: [
        _jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_1__.IMainMenu,
        _jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_2__.IDocumentManager,
        _jupyterlab_statusbar__WEBPACK_IMPORTED_MODULE_0__.IStatusBar
    ],
    autoStart: true,
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (rspExtension);


/***/ }),

/***/ "./lib/query.js":
/*!**********************!*\
  !*** ./lib/query.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "CommandIDs": () => (/* binding */ CommandIDs),
/* harmony export */   "activateRSPQueryExtension": () => (/* binding */ activateRSPQueryExtension),
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/mainmenu */ "webpack/sharing/consume/default/@jupyterlab/mainmenu");
/* harmony import */ var _jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @jupyterlab/docmanager */ "webpack/sharing/consume/default/@jupyterlab/docmanager");
/* harmony import */ var _jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @jupyterlab/services */ "webpack/sharing/consume/default/@jupyterlab/services");
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_services__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @jupyterlab/coreutils */ "webpack/sharing/consume/default/@jupyterlab/coreutils");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var _tokens__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ./tokens */ "./lib/tokens.js");
// Copyright (c) LSST DM/SQuaRE
// Distributed under the terms of the MIT License.








/**
 * The command IDs used by the plugin.
 */
var CommandIDs;
(function (CommandIDs) {
    CommandIDs.rubinquery = 'rubinquery';
})(CommandIDs || (CommandIDs = {}));
;
/**
 * Activate the extension.
 */
function activateRSPQueryExtension(app, mainMenu, docManager) {
    console.log('rsp-query...loading');
    let svcManager = app.serviceManager;
    const { commands } = app;
    commands.addCommand(CommandIDs.rubinquery, {
        label: 'Open from portal query URL...',
        caption: 'Open notebook from supplied portal query URL',
        execute: () => {
            rubinportalquery(app, docManager, svcManager);
        }
    });
    // Add commands and menu itmes.
    let menu = { command: CommandIDs.rubinquery };
    let rubinmenu = new _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__.Menu({
        commands,
    });
    rubinmenu.title.label = "Rubin";
    rubinmenu.insertItem(0, menu);
    mainMenu.addMenu(rubinmenu);
    console.log('rsp-query...loaded');
}
class QueryHandler extends _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__.Widget {
    constructor() {
        super({ node: Private.createQueryNode() });
        this.addClass('rubin-qh');
    }
    get inputNode() {
        return this.node.getElementsByTagName('input')[0];
    }
    getValue() {
        return this.inputNode.value;
    }
}
function queryDialog(manager) {
    let options = {
        title: 'Query Value',
        body: new QueryHandler(),
        focusNodeSelector: 'input',
        buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.Dialog.cancelButton(), _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.Dialog.okButton({ label: 'CREATE' })]
    };
    return (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.showDialog)(options).then(result => {
        if (!result) {
            console.log("No result from queryDialog");
            return new Promise((res, rej) => { });
        }
        console.log("Result from queryDialog: ", result);
        if (!result.value) {
            console.log("No result.value from queryDialog");
            return new Promise((res, rej) => { });
        }
        if (result.button.label === 'CREATE') {
            console.log("Got result ", result.value, " from queryDialog: CREATE");
            return Promise.resolve(result.value);
        }
        console.log("Did not get queryDialog: CREATE");
        return new Promise((res, rej) => { });
    });
}
function apiRequest(url, init, settings) {
    /**
    * Make a request to our endpoint to get a pointer to a templated
    *  notebook for a given query
    *
    * @param url - the path for the query extension
    *
    * @param init - The POST + body for the extension
    *
    * @param settings - the settings for the current notebook server.
    *
    * @returns a Promise resolved with the JSON response
    */
    // Fake out URL check in makeRequest
    let newSettings = _jupyterlab_services__WEBPACK_IMPORTED_MODULE_4__.ServerConnection.makeSettings({
        baseUrl: settings.baseUrl,
        appUrl: settings.appUrl,
        wsUrl: settings.wsUrl,
        init: settings.init,
        token: settings.token,
        Request: settings.Request,
        Headers: settings.Headers,
        WebSocket: settings.WebSocket
    });
    return _jupyterlab_services__WEBPACK_IMPORTED_MODULE_4__.ServerConnection.makeRequest(url, init, newSettings).then(response => {
        if (response.status !== 200) {
            return response.json().then(data => {
                throw new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_4__.ServerConnection.ResponseError(response, data.message);
            });
        }
        return response.json();
    });
}
function rubinportalquery(app, docManager, svcManager) {
    queryDialog(docManager).then(url => {
        console.log("Query URL is", url);
        if (!url) {
            console.log("Query URL was null");
            return new Promise((res, rej) => { });
        }
        let body = JSON.stringify({
            "type": "portal",
            "value": url
        });
        let endpoint = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_5__.PageConfig.getBaseUrl() + "rubin/query";
        let init = {
            method: "POST",
            body: body
        };
        let settings = svcManager.serverSettings;
        apiRequest(endpoint, init, settings).then(function (res) {
            let path = res.path;
            docManager.open(path);
        });
        return new Promise((res, rej) => { });
    });
}
/**
 * Initialization data for the jupyterlab-lsstquery extension.
 */
const rspQueryExtension = {
    activate: activateRSPQueryExtension,
    id: _tokens__WEBPACK_IMPORTED_MODULE_6__.QUERY_ID,
    requires: [
        _jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_2__.IMainMenu,
        _jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_3__.IDocumentManager
    ],
    autoStart: false,
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (rspQueryExtension);
var Private;
(function (Private) {
    /**
     * Create node for query handler.
     */
    function createQueryNode() {
        let body = document.createElement('div');
        let qidLabel = document.createElement('label');
        qidLabel.textContent = 'Enter Query Value';
        let name = document.createElement('input');
        body.appendChild(qidLabel);
        body.appendChild(name);
        return body;
    }
    Private.createQueryNode = createQueryNode;
})(Private || (Private = {}));


/***/ }),

/***/ "./lib/savequit.js":
/*!*************************!*\
  !*** ./lib/savequit.js ***!
  \*************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "CommandIDs": () => (/* binding */ CommandIDs),
/* harmony export */   "activateRSPSavequitExtension": () => (/* binding */ activateRSPSavequitExtension),
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/mainmenu */ "webpack/sharing/consume/default/@jupyterlab/mainmenu");
/* harmony import */ var _jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/docmanager */ "webpack/sharing/consume/default/@jupyterlab/docmanager");
/* harmony import */ var _jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @jupyterlab/coreutils */ "webpack/sharing/consume/default/@jupyterlab/coreutils");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @jupyterlab/services */ "webpack/sharing/consume/default/@jupyterlab/services");
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_services__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _lumino_algorithm__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @lumino/algorithm */ "webpack/sharing/consume/default/@lumino/algorithm");
/* harmony import */ var _lumino_algorithm__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(_lumino_algorithm__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var _tokens__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ./tokens */ "./lib/tokens.js");
// Copyright (c) LSST DM/SQuaRE
// Distributed under the terms of the MIT License.







/**
 * The command IDs used by the plugin.
 */
var CommandIDs;
(function (CommandIDs) {
    CommandIDs.saveQuit = 'savequit:savequit';
    CommandIDs.justQuit = 'justquit:justquit';
})(CommandIDs || (CommandIDs = {}));
;
/**
 * Activate the jupyterhub extension.
 */
function activateRSPSavequitExtension(app, mainMenu, docManager) {
    console.log('rsp-savequit: loading...');
    let svcManager = app.serviceManager;
    const { commands } = app;
    commands.addCommand(CommandIDs.saveQuit, {
        label: 'Save All and Exit',
        caption: 'Save open notebooks and destroy container',
        execute: () => {
            saveAndQuit(app, docManager, svcManager);
        }
    });
    commands.addCommand(CommandIDs.justQuit, {
        label: 'Exit Without Saving',
        caption: 'Destroy container',
        execute: () => {
            justQuit(app, docManager, svcManager);
        }
    });
    // Add commands and menu itmes.
    let menu = [
        { command: CommandIDs.saveQuit },
        { command: CommandIDs.justQuit },
    ];
    // Put it at the bottom of file menu
    let rank = 150;
    mainMenu.fileMenu.addGroup(menu, rank);
    console.log('rsp-savequit: ...loaded.');
}
function hubDeleteRequest(app) {
    let svcManager = app.serviceManager;
    let settings = svcManager.serverSettings;
    let endpoint = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_3__.PageConfig.getBaseUrl() + "rubin/hub";
    let init = {
        method: "DELETE",
    };
    console.log("hubRequest: URL: ", endpoint, " | Settings:", settings);
    return _jupyterlab_services__WEBPACK_IMPORTED_MODULE_4__.ServerConnection.makeRequest(endpoint, init, settings);
}
function saveAll(app, docManager, svcManager) {
    let promises = [];
    (0,_lumino_algorithm__WEBPACK_IMPORTED_MODULE_5__.each)(app.shell.widgets('main'), widget => {
        if (widget) {
            let context = docManager.contextForWidget(widget);
            if (context) {
                console.log("Saving context for widget:", { id: widget.id });
                promises.push(context.save());
            }
            else {
                console.log("No context for widget:", { id: widget.id });
            }
        }
    });
    console.log("Waiting for all save-document promises to resolve.");
    let r = Promise.resolve(1);
    if (promises) {
        Promise.all(promises);
        r = promises[0];
    }
    return r;
}
function saveAndQuit(app, docManager, svcManager) {
    infoDialog();
    const retval = Promise.resolve(saveAll(app, docManager, svcManager));
    retval.then((res) => {
        return justQuit(app, docManager, svcManager);
    });
    retval.catch((err) => {
        console.log("saveAll failed: ", err.message);
    });
    console.log("Save and Quit complete.");
    return retval;
}
function justQuit(app, docManager, svcManager) {
    infoDialog();
    let targetEndpoint = "/";
    return Promise.resolve(hubDeleteRequest(app)
        .then(() => {
        console.log("Quit complete.");
    })
        .then(() => {
        window.location.replace(targetEndpoint);
    }));
}
function infoDialog() {
    let options = {
        title: "Redirecting to landing page",
        body: "JupyterLab cleaning up and redirecting to landing page.",
        buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Dialog.okButton({ label: 'Got it!' })]
    };
    return (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.showDialog)(options).then(() => {
        console.log("Info dialog panel displayed");
    });
}
/**
 * Initialization data for the rspSavequit extension.
 */
const rspSavequitExtension = {
    activate: activateRSPSavequitExtension,
    id: _tokens__WEBPACK_IMPORTED_MODULE_6__.SAVEQUIT_ID,
    requires: [
        _jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_1__.IMainMenu,
        _jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_2__.IDocumentManager
    ],
    autoStart: false,
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (rspSavequitExtension);


/***/ }),

/***/ "./lib/tokens.js":
/*!***********************!*\
  !*** ./lib/tokens.js ***!
  \***********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "NS": () => (/* binding */ NS),
/* harmony export */   "PLUGIN_ID": () => (/* binding */ PLUGIN_ID),
/* harmony export */   "DISPLAYVERSION_ID": () => (/* binding */ DISPLAYVERSION_ID),
/* harmony export */   "SAVEQUIT_ID": () => (/* binding */ SAVEQUIT_ID),
/* harmony export */   "QUERY_ID": () => (/* binding */ QUERY_ID)
/* harmony export */ });
/**
 * Namespace for everything
 */
/*import { Token } from '@lumino/coreutils';*/
const NS = 'rsp-jupyterlab';
const PLUGIN_ID = `${NS}:plugin`;
const DISPLAYVERSION_ID = `${NS}:displayversion`;
const SAVEQUIT_ID = `${NS}:savequit`;
const QUERY_ID = `${NS}:query`;


/***/ })

}]);
//# sourceMappingURL=lib_index_js.e0bf8ba868c627d5e57b.js.map