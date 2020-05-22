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
/**
 * This file definish actions functions that will call specifics sagas with the needed parameters
 */

/**
 * Call the saga SAGA_LIST_STATIFICATIONS with the needed parameters
 * @param  {[type]} limit the number of statification to show/get per page in the list
 * @param  {[type]} skip  the number of statification to skip before requesting new statification
 */
export const listStatifications = (limit, skip) => ({
  type: 'SAGA_LIST_STATIFICATIONS',
  limit,
  skip
})

/**
 * Call the saga SAGA_LIST_STATIFICATIONS_COUNT
 */
export const countStatifications = () => ({
  type: 'SAGA_LIST_STATIFICATIONS_COUNT'
})

/**
 * Call the saga SAGA_STATIFICATION_SUBMIT_FORM with the needed parameters
 * @param  {[type]} data contain the designation and description of the statification set in the form
 */
export const statificationsSubmitForm = data => ({
  type: 'SAGA_STATIFICATION_SUBMIT_FORM',
  data
})

/**
 * Call the saga SAGA_STATIFICATION_CHECK_STATUS with the needed parameters
 * @param  {[type]} step the step that is currently set in the application
 * @param  {[type]} waitForServer if client is waiting for the server
 */
export const statificationsCheckStatus = (step, waitForServer) => {
  return ({
    type: 'SAGA_STATIFICATION_CHECK_STATUS',
    step,
    waitForServer
  })
}

/**
* Call the saga SAGA_STATIFICATION_STOP_PROCESS
 */
export const statificationsStopProcess = () => ({
  type: 'SAGA_STATIFICATION_STOP_PROCESS'
})

/**
 * Call the saga SAGA_STATIFICATION_LOAD_DATA with the needed parameters
 * @param  {[type]} sha the archive sha of the statification to load
 */
export const statificationsLoadData = sha => ({
  type: 'SAGA_STATIFICATION_LOAD_DATA',
  sha
})

/**
 * Call the saga SAGA_STATIFICATION_CHECK_CURRENT_LOG
 */
export const statificationsCheckCurrentLog = () => ({
  type: 'SAGA_STATIFICATION_CHECK_CURRENT_LOG'
})

/**
 * Call the saga SAGA_STATIFICATION_SAVE
 */
export const statificationsSave = () => ({
  type: 'SAGA_STATIFICATION_SAVE'
})

/**
 * Call the saga SAGA_STATIFICATION_PUSH_TO_PROD with the needed parameters
 * @param  {[type]} sha the archive sha of the statification to push to production
 */
export const statificationsPushToProd = sha => ({
  type: 'SAGA_STATIFICATION_PUSH_TO_PROD',
  sha
})

/**
 * Call the saga SAGA_STATIFICATION_VISUALIZE with the needed parameters
 * @param  {[type]} sha the archive sha of the statification to push to production
 */
export const statificationsVisualize = sha => ({
  type: 'SAGA_STATIFICATION_VISUALIZE',
  sha
})
