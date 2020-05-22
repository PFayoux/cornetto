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
 * Set a new error in the list of error
 * @param  {String} message       The message of the error
 * @param  {String} [severity='error'] The level of severity of the error
 */
export const pushError = (message, severity = 'error') => ({
  type: 'ERROR_PUSH',
  message,
  severity
})

/**
 * Dismiss the error at the given position
 * @param  {[type]} position the index of the error
 */
export const dismissError = position => ({
  type: 'ERROR_DISMISS',
  position
})

/**
 * Clear all errors
 */
export const clearErrors = () => ({
  type: 'ERROR_CLEAR_ALL'
})
