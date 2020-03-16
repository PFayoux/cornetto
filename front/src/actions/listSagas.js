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
