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
import { pushError } from '../actions/errors'
import { getErrorMessage } from '../utils'
import { setList, setLoading, setCount } from '../actions/statifications'

/**
 *
 * Do the request to get the list of statification
 * @param  {number} limit the maximum of statification to get
 * @param  {number} skip  the number of statification to skip in the query
 * @return {Array}       return an Array of statification Object
 */
async function listStatifications (limit, skip) {
  try {
    const url = `/api/statification/list?limit=${limit}&skip=${skip}`
    const response = await fetch(url, {
      method: 'POST',
      credentials: 'same-origin'
    })
    const data = await response.json()
    if (data.success === false) {
      throw new Error(data.error)
    } else {
      return data.statifications
    }
  } catch (error) {
    console.log(error)
    throw error
  }
}

/**
 * This Saga will get the list of statification
 * @param  {Object}    action the action object that triggered the Saga
 */
function * listStatificationsSaga (action) {
  try {
    yield put(setLoading(true))

    const { result, timeout } = yield race({
      result: call(listStatifications, action.limit, action.skip),
      timeout: delay(20000)
    })

    if (timeout) {
      throw new Error('timeout')
    }

    yield put(setLoading(false))
    // set the list inside the statifications reducer
    yield put(setList(result))
  } catch (error) {
    yield put(setLoading(false))
    yield put(pushError(getErrorMessage(error)))
  }
}

/**
 *
 * Do the request to get the number of statification
 * @return {number} return the number of statification in the database
 */
async function countStatifications () {
  try {
    const url = '/api/statification/count'
    const response = await fetch(url, {
      method: 'POST',
      credentials: 'same-origin'
    })
    const data = await response.json()
    if (data.success === false) {
      throw new Error(data.error)
    } else {
      return data.count
    }
  } catch (error) {
    console.log(error)
    throw error
  }
}

/**
 * This Saga will get the number of Statification
 * @param  {Object}    action the action object that triggered the Saga
 */
function * countStatificationsSaga (action) {
  try {
    const { result, timeout } = yield race({
      result: call(countStatifications),
      timeout: delay(20000)
    })
    if (timeout) {
      throw new Error('timeout')
    }

    yield put(setCount(result))
  } catch (error) {
    yield put(pushError(getErrorMessage(error)))
  }
}

function * watchListSagas () {
  yield takeEvery('SAGA_LIST_STATIFICATIONS', listStatificationsSaga)
  yield takeEvery('SAGA_LIST_STATIFICATIONS_COUNT', countStatificationsSaga)
}

export default watchListSagas
