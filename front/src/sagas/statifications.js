/*
 Cornetto

 Copyright (C)  2018–2020 ANSSI
 Contributors:
 2018–2020 Bureau Applicatif tech-sdn-app@ssi.gouv.fr
 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.
 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 GNU General Public License for more details.
 You should have received a copy of the GNU General Public License
 */
import { takeEvery, put, call, race, delay } from 'redux-saga/effects'
import { I18n } from 'react-redux-i18n'
import { pushError } from '../actions/errors'
import { getErrorMessage, getInfoMessage } from '../utils'

import {
  setFormData, setFormErrors, setFormLoading, setLoading, setWaitForServer,
  setListInfoLoading, setListErrorsTypeMime, setListScrapyErrors, setListHtmlErrors,
  setListScannedFiles, setListExternalLinks, setListStatificationHistorics,
  setStatificationRunning, setStatificationProgress, setActiveStep, setsha,
  setListErrorErrorsTypeMime, setListErrorScrapyErrors, setListErrorHtmlErrors,
  setListErrorScannedFiles, setListErrorExternalLinks, setListErrorStatificationHistorics,
  clearListErrorInfo, setClearInterval
}
  from '../actions/statifications'
import { setDialogOpen, setDialogTitle, setDialogText, setDialogTypeAction } from '../actions/dialog'
import { statificationsCheckCurrentLog, statificationsLoadData } from '../actions/statificationSagas'
import { listStatifications, countStatifications } from '../actions/listSagas'

/**
 * Do the request to load the data of a statification
 * @param  {string} sha the archive sha of the statification to get
 * @return {Object}     json object of the statification
 */
async function loadData (sha) {
  try {
    // send the query
    const response = await fetch(`/api/statification?sha=${sha}`, {
      method: 'POST',
      credentials: 'same-origin'
    })

    const data = await response.json()
    if (data.success !== false) {
      return data
    } else {
      throw new Error(data.error)
    }
  } catch (error) {
    console.log(error)
    throw error
  }
}

/**
 * This Saga will get a Statification object from the API given an archive sha,
 * then load the datas of the statification into the page that list the informations
 * @param  {Object}    action the action object that triggered the Saga
 *                            it should have the following attributes :
 *                             - {string} sha : the archive sha of the statification to load
 */
function * loadDataSaga (action) {
  try {
    // show the loading gif in the infos list
    yield put(setListInfoLoading(true))

    // do a race between loadData and delay, and store the result respectively in result and timeout
    const { result, timeout } = yield race({
      // call loadData to do the request with the parameter 'sha' passed with the action
      result: call(loadData, action.sha),

      // define the timeout in case the server take too long to answer
      timeout: delay(20000)
    })

    // if we reach the timeout then throw an error
    if (timeout) { throw new Error('timeout') }

    // put the statification returned by the server in the form
    yield put(setFormData(result.statification))

    // empty the error field of the form
    yield put(setFormErrors([]))

    // if there is an array of errors type mime, we set the errors in the list associated
    if (result.errors_type_mime !== undefined) {
      yield put(setListErrorsTypeMime(result.errors_type_mime))
    }

    // if there is an array of scrapy erros, we set the errors in the list associated
    if (result.scrapy_errors !== undefined) {
      yield put(setListScrapyErrors(result.scrapy_errors))
    }

    // if there is an array of html errors, we set the errors in the list associated
    if (result.html_errors !== undefined) {
      yield put(setListHtmlErrors(result.html_errors))
    }

    // if there is an array of scanned files, we set the errors in the list associated
    if (result.scanned_files !== undefined) {
      yield put(setListScannedFiles(result.scanned_files))
    }

    // if there is an array of external links, we set the errors in the list associated
    if (result.external_links !== undefined) {
      yield put(setListExternalLinks(result.external_links))
    }

    // if there is an array of historic, we set the errors in the list associated
    if (result.statification_historics !== undefined) {
      yield put(setListStatificationHistorics(result.statification_historics))
    }
    // catch the HTML error send by the server
  } catch (error) {
    // print a corresponding message to the user
    yield put(pushError(getErrorMessage(error)))
  } finally {
    // hide the loading gif in the infos list
    yield put(setListInfoLoading(false))
  }
}

/**
 * Do the request to get the status of the API
 * @return {Object} the Object containing all the informations about the state of the API.
 * The Object will contain the following attributes :
    - isRunning         :   a boolean that indicate if a statification Process is running
    - sha               :   a string that contain the sha of the last statification,
                            if the last is a new and unsaved statification it will be empty
    - designation       :   the designation of the last statification, or empty
    - description       :   the description of the last statification, or empty
    - status            :   the status of the last statification :  CREATED = 0
                                                                    STATIFIED = 1
                                                                    SAVED = 2
                                                                    PRODUCTION = 3
                                                                    VISUALIZED = 4
                            Default status will be 3, if there is no statification in the database the user will still
                            be able to create a new one, if there are ongoing statification to be push to prod it still
                            give the hand to the user that have saved it.
    - i_nb_item_to_crawl :  the number of item that have been crawled during the last statification, it will be used
                            as a reference of the number of items to crawl to the next statification. If there is no
                            statification in the database it will be set to 100 by default.
    **Example**:

      The default status when launching the api for the first time should be this one.
      {
          'isRunning': false,
          'sha': '',
          'designation': '',
          'description': '',
          'currentNbItemCrawled': 0,
          'nbItemToCrawl': 100,
          'status': 3,
          'isLocked': false,
          'statusBackground': {}
      }
 */
async function checkStatusAPI () {
  try {
    const response = await fetch('/api/statification/status', {
      method: 'POST',
      credentials: 'same-origin',
      headers: new Headers({ 'Content-Type': 'application/json' })
    })

    const data = await response.json()
    if (data.success === false) {
      throw new Error(data.error)
    } else {
      return data
    }
  } catch (error) {
    console.log(error)
    throw error
  }
}

/**
 * This Saga will get the status of the the API
 * @param  {Object}    action the action object that triggered the Saga
 *                            It should contain the following attributes:
 *                             - {boolean} waitForServer : a boolean to know if we are waiting for the server to finish a long action (like save, visualize...).
 */
function * checkStatusAPISaga (action) {
  try {
    // send the submit request to the server
    const { result, timeout } = yield race({
      result: call(checkStatusAPI),
      timeout: delay(8000)
    })
    if (timeout) {
      throw new Error('timeout')
    }

    // open a popup and send user to create page if status is not 3 (published) or 2 (saved) or visualized
    if (result.status !== 4 && result.status !== 3 && result.status !== 2 && window.location.pathname.search('list') >= 0) {
      // setup the dialog and show it to the user
      yield put(setDialogTitle(I18n.t('statification.dialog.redirect_process_running.title')))
      yield put(setDialogText(I18n.t('statification.dialog.redirect_process_running.text')))
      yield put(setDialogTypeAction('redirect_process_running'))
      yield put(setDialogOpen(true))
    }

    // if a background process has trigger an error
    if (action.waitForServer === true && result.statusBackground && !result.statusBackground.success && result.statusBackground.error) {
      // print a corresponding message to the user
      yield put(pushError(getErrorMessage(result.statusBackground.error), 'warn'))
      // if a background process has terminated then remove loading wheel
      yield put(setLoading(false))
      yield put(setWaitForServer(false))
    } else if (action.waitForServer === true && result.statusBackground && result.statusBackground.success && result.statusBackground.operation) {
      // if a background process has finished
      yield put(pushError(getInfoMessage(result.statusBackground.operation), 'info'))
      // if a background process has terminated then remove loading wheel
      yield put(setLoading(false))
      yield put(setWaitForServer(false))
    }

    // if a background process that return a archive sha has finished
    if (result.statusBackground && result.statusBackground.sha) {
      // register the archive sha of the last saved statification
      yield put(setsha(result.statusBackground.sha))
    } else {
      // register the archive sha of the last statification
      yield put(setsha(result.sha))
    }

    // if the process is running
    if (result.isRunning) {
      // if a process is running then user should be on step 0
      yield put(setActiveStep(0))
      //  add the progressbar in the form
      yield put(setStatificationRunning(true))
      yield put(setStatificationProgress(result.currentNbItemCrawled, result.nbItemToCrawl))
      // set the designation and description of the current statification
      yield put(setFormData({ designation: result.designation, description: result.description }))
    } else {
      // when the statification process is finished and if current step is not 1 and not 2, check the logs of the statification
      if (result.status === 1 && action.step !== 1 && action.step !== 2) {
        yield put(statificationsCheckCurrentLog())
      } else if (action.waitForServer === true && result.statusBackground && result.statusBackground.success && result.statusBackground.operation === 'pushtoprod' && result.statusBackground.sha) {
        // case pushToProd
        // refresh the list and count
        yield put(countStatifications())
        yield put(listStatifications())
        // refresh list statification
        yield put(statificationsLoadData(result.statusBackground.sha))
        // redirect user to step 0
        yield put(setActiveStep(0))
        // open in a new tab the push to prod statification
        yield window.open(I18n.t('url.site_prod'), '_blanck').focus()
      } else if (action.waitForServer === true && result.statusBackground && result.statusBackground.success && result.statusBackground.operation === 'visualize' && result.statusBackground.sha) {
        // refresh the list and count
        yield put(countStatifications())
        yield put(listStatifications())
        // refresh visualized statification
        yield put(statificationsLoadData(result.statusBackground.sha))
        // open in a new tab the visualized statification
        yield window.open(I18n.t('url.site_visualize'), '_blank').focus()
      } else if (result.status === 2 && result.statusBackground && result.statusBackground.success && result.statusBackground.operation === 'save' && action.step === 2) {
        // case save finish user in step 2
        // if status is 2, statusBackground is success and operation is save, it means the save operations has finished so if we are in step 2 we need to pass to step 3
        yield put(setActiveStep(3))
        // clear the list of error after an operation of save
        yield put(clearListErrorInfo())
      } else if ((result.status === 2 && result.statusBackground && result.statusBackground.success && result.statusBackground.operation === 'save' && action.step !== 3)) {
        // case save finish user not in step 2 and not in step 3
        // if the status is 2 (saved) and not in step 3 (push to prod button), or if status is 3 (pushed to prod) then the step should be 0
        yield put(setActiveStep(0))
        // clear the list of error after an operation of save
        yield put(clearListErrorInfo())
      }

      //  remove the progressbar in the form
      yield put(setStatificationRunning(false))
      yield put(setStatificationProgress(0, result.nbItemToCrawl))
    }
    // catch the HTML error send by the server
  } catch (error) {
    // print a corresponding message to the user
    yield put(pushError(getErrorMessage(error), 'warn'))
  }
}

/**
 * Do the request to submit the form to create a new statification
 * and start the statification process.
 * @param  {Object} data the data of the form.
 *                       It should contain the following attributes :
 *                        - designation : the designation of the statification
 *                        - description : the description of the statification
 * @return {boolean}     return true if the operation is successful
 */
async function submitForm (dataToSend) {
  try {
    const response = await fetch('/api/statification/start', {
      method: 'POST',
      credentials: 'same-origin',
      headers: new Headers({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(dataToSend)
    })
    const data = await response.json()
    if (data.success === false) {
      throw new Error(data.error)
    } else {
      return data.success
    }
  } catch (error) {
    console.log(error)
    throw error
  }
}

/**
 * This Saga will manage  method send the form to the API and start the statification process
 * @param  {Object}    action the action object that triggered the Saga.
 *                            It should contain the following attributes :
 *                             - data : the object that contain the designation
 *                                      and description of the statification
 */
function * submitFormSaga (action) {
  try {
    // set the loading wheel in the form
    yield put(setFormLoading(true))
    yield put(setLoading(true))

    // send the submit request to the server
    const { result, timeout } = yield race({
      result: call(submitForm, action.data),
      timeout: delay(120000)
    })
    if (timeout) { throw new Error('timeout') }
    // if the process has started
    if (result) {
      // set the progressbar in the form
      yield put(setStatificationRunning(true))
    }
    // catch the HTML error send by the server
  } catch (error) {
    if (error === 'route_access') {
      // print a corresponding message to the user
      yield put(pushError(getErrorMessage(error), 'warn'))
    } else {
    // print a corresponding message to the user
      yield put(pushError(getErrorMessage(error)))
    }
  } finally {
    // stop the loading wheel
    yield put(setFormLoading(false))
    yield put(setLoading(false))
  }
}

/**
 *
 * Do the request to stop the statification process
 * @return {Object} return true if there was no error on the API side
 */
async function stopProcess () {
  try {
    const response = await fetch('/api/statification/stop', {
      method: 'POST',
      credentials: 'same-origin',
      headers: new Headers({ 'Content-Type': 'application/json' })
    })
    const data = await response.json()
    if (data.success === false) {
      throw new Error(data.error)
    } else {
      return data.success
    }
  } catch (error) {
    console.log(error)
    throw error
  }
}

/**
 * This Saga will stop the statification process
 */
function * stopProcessSaga () {
  try {
    // set the loading wheel in the stepper
    yield put(setLoading(true))

    // send the submit request to the server
    const { result, timeout } = yield race({
      result: call(stopProcess),
      timeout: delay(120000)
    })
    if (timeout) {
      throw new Error('timeout')
    }

    // if result is not true, an error happend somewhere
    if (!result) {
      throw new Error('unknown')
    }

    // catch the HTML error send by the server
  } catch (error) {
    // print a corresponding message to the user
    yield put(pushError(getErrorMessage(error)))
  } finally {
    // remove the loading wheel in the stepper
    yield put(setFormLoading(false))
    yield put(setLoading(false))
    yield put(setDialogOpen(false))
  }
}

/**
 * Do the request to save the new statification
 * @return {Object} true if no error occured, otherwise will throw an error
 */
async function save () {
  try {
    const response = await fetch('/api/statification/save', {
      method: 'POST',
      credentials: 'same-origin'
    })
    const data = await response.json()
    if (data.success === false) {
      throw new Error(data.error)
    } else {
      return data.success
    }
  } catch (error) {
    console.log(error)
    throw error
  }
}

/**
 * This Saga will save a statification by creating an archive with
 * the source of the statification
 */
function * saveSaga () {
  // set the loading wheel in the stepper
  yield put(setLoading(true))
  yield put(setWaitForServer(true))
  // clear all the interval that have been set
  yield put(setClearInterval(true))

  try {
    // send the submit request to the server
    const { result, timeout } = yield race({
      result: call(save),
      timeout: delay(120000)
    })
    if (timeout) { throw new Error('timeout') }

    // restart setInterval
    yield put(setClearInterval(false))

    // catch the error
    if (!result.success) {
      throw new Error(result.error)
    }

    // show a message to the user to indicate action has been launched
    yield put(pushError(getInfoMessage('start_save'), 'info'))
  } catch (error) {
    yield put(setLoading(false))
    if (error === 'save_nothing') {
      yield put(pushError(getErrorMessage(error), 'warn'))
      yield put(setActiveStep(0))
    } else if (error === 'route_access') {
      // print a corresponding message to the user
      yield put(pushError(getErrorMessage(error), 'warn'))
      yield put(setActiveStep(0))
    } else {
      // print a corresponding message to the user
      yield put(pushError(getErrorMessage(error)))
    }
  }
}

/**
 * Will manage the request to the API to push the statification into production
 * @param  {string} sha   the archive sha of the statification to publish to production
 */
async function pushToProd (sha) {
  try {
    const response = await fetch(`/api/statification/pushtoprod?sha=${sha}`, {
      method: 'POST',
      credentials: 'same-origin'
    })
    const data = await response.json()
    if (data.success === false) {
      throw new Error(data.error)
    } else {
      return data
    }
  } catch (error) {
    console.log(error)
    throw error
  }
}

/**
 * This Saga will push into production the given statification
 * @param  {Object}    action the action object that triggered the Saga.
 *                            It should contain the following attributes :
 *                             - sha : the sha of the statification to push into production
 */
function * pushToProdSaga (action) {
  // set the loading wheel in the stepper
  yield put(setLoading(true))
  yield put(setWaitForServer(true))
  // clear all the interval that have been set
  yield put(setClearInterval(true))

  try {
    // send the submit request to the server
    const { result, timeout } = yield race({
      result: call(pushToProd, action.sha),
      timeout: delay(120000)
    })
    if (timeout) {
      throw new Error('timeout')
    }

    // restart setInterval
    yield put(setClearInterval(false))

    // if the statification has not been push to prod successfully
    if (!result.success) {
      throw new Error('pushtoprod')
    }

    yield put(pushError(getInfoMessage('start_pushtoprod'), 'info'))

    // catch the HTML error send by the server
  } catch (error) {
    yield put(setLoading(false))
    if (error === 'route_access') {
      // print a corresponding message to the user
      yield put(pushError(getErrorMessage(error), 'warn'))
      yield put(setActiveStep(0))
    } else {
    // print a corresponding message to the user
      yield put(pushError(getErrorMessage(error)))
    }
  }
}

/**
 * Do the request to save the statification
 * @param  {string} sha  the archive sha of the statification to visualize
 */
async function visualize (sha) {
  try {
    const response = await fetch(`/api/statification/visualize?sha=${sha}`, {
      method: 'POST',
      credentials: 'same-origin'
    })
    const data = await response.json()
    if (data.success === false) {
      throw new Error(data.error)
    } else {
      return data
    }
  } catch (error) {
    console.log(error)
    throw error
  }
}

/**
 * This Saga will deploy the wanted statification in the visualize directory
 * @param  {Object}    action the action object that triggered the Saga.
 */
function * visualizeSaga (action) {
  yield put(setLoading(true))
  yield put(setWaitForServer(true))
  // clear all the interval that have been set
  yield put(setClearInterval(true))

  try {
    // send the submit request to the server
    const { result, timeout } = yield race({
      result: call(visualize, action.sha),
      timeout: delay(120000)
    })
    if (timeout) { throw new Error('timeout') }

    // restart setInterval
    yield put(setClearInterval(false))

    // if the statification has not been push to prod successfully
    if (!result.success) {
      yield put(pushError(I18n.t('errors.text.visualize')))
    }

    yield put(pushError(getInfoMessage('start_visualize'), 'info'))

    // catch the HTML error send by the server
  } catch (error) {
    yield put(setLoading(false))
    if (error === 'route_access') {
      // print a corresponding message to the user
      yield put(pushError(getErrorMessage(error), 'warn'))
      yield put(setActiveStep(0))
    } else {
    // print a corresponding message to the user
      yield put(pushError(getErrorMessage(error)))
    }
  }
}

/**
 * Manage the request to get the information of the new statification
 * @return {Object} return an object containing the information of the new statification
 */
async function checkLogCurrentStatification () {
  try {
    const response = await fetch('/api/statification/current', {
      method: 'POST',
      credentials: 'same-origin'
    })
    // get json from response
    const data = await response.json()
    if (data.success === false) {
      throw new Error(data.error)
    } else {
      return data
    }
  } catch (error) {
    console.log(error)
    throw error
  }
}

/**
 * This Saga will get the information about the new statification, 
 * it concern the errors that occured during the statification process 
 * and the information like the mime type of file that have been crawled.
 */
function * checkLogCurrentStatificationSaga () {
  try {
    // send the submit request to the server
    const { result, timeout } = yield race({
      result: call(checkLogCurrentStatification),
      timeout: delay(20000)
    })
    if (timeout) { throw new Error('timeout') }

    // limit of the number of error accepted
    if (result && (result.html_errors.length > 500 || result.scrapy_errors.length > 500)) {
      // if there is an array of errors type mime, we set the errors in the list associated
      if (result.errors_type_mime !== undefined) {
        yield put(setListErrorErrorsTypeMime(result.errors_type_mime))
      }

      // if there is an array of scrapy erros, we set the errors in the list associated
      if (result.scrapy_errors !== undefined) {
        yield put(setListErrorScrapyErrors(result.scrapy_errors))
      }

      // if there is an array of html errors, we set the errors in the list associated
      if (result.html_errors !== undefined) {
        yield put(setListErrorHtmlErrors(result.html_errors))
      }

      // if there is an array of scanned files, we set the errors in the list associated
      if (result.scanned_files !== undefined) {
        yield put(setListErrorScannedFiles(result.scanned_files))
      }

      // if there is an array of external links, we set the errors in the list associated
      if (result.external_links !== undefined) {
        yield put(setListErrorExternalLinks(result.external_links))
      }

      // if there is an array of historic, we set the errors in the list associated
      if (result.statification_historics !== undefined) {
        yield put(setListErrorStatificationHistorics(result.statification_historics))
      }
    }
    // catch the HTML error send by the server
  } catch (error) {
    // print a corresponding message to the user
    yield put(pushError(getErrorMessage(error)))
  } finally {
    // set next step (Préliser)
    yield put(setActiveStep(1))
    yield put(setLoading(false))
  }
}

/**
 * Define the SAGAs
 * @return {Generator} [description]
 */
function * watchStatificationsSagas () {
  yield takeEvery('SAGA_STATIFICATION_SUBMIT_FORM', submitFormSaga)
  yield takeEvery('SAGA_STATIFICATION_STOP_PROCESS', stopProcessSaga)
  yield takeEvery('SAGA_STATIFICATION_LOAD_DATA', loadDataSaga)
  yield takeEvery('SAGA_STATIFICATION_CHECK_STATUS', checkStatusAPISaga)
  yield takeEvery('SAGA_STATIFICATION_SAVE', saveSaga)
  yield takeEvery('SAGA_STATIFICATION_PUSH_TO_PROD', pushToProdSaga)
  yield takeEvery('SAGA_STATIFICATION_VISUALIZE', visualizeSaga)
  yield takeEvery('SAGA_STATIFICATION_CHECK_CURRENT_LOG', checkLogCurrentStatificationSaga)
}

export default watchStatificationsSagas
