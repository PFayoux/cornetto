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
import { connect } from 'react-redux'

import StatificationCreate from '../../components/statifications/StatificationCreate'

import { setActiveStep, newForm } from '../../actions/statifications'
import { statificationsSave, statificationsPushToProd } from '../../actions/statificationSagas'
import { setDialogOpen, setDialogTitle, setDialogText, setDialogTypeAction } from '../../actions/dialog'

const mapStateToProps = (state, props) => ({
  activeStep: state.statifications.get('activeStep', 0),
  statificationsSaveData: state.statifications.get('statificationsSaveData'),
  currentStatificationsha: state.statifications.get('sha'),
  loading: state.statifications.get('loading')
})

const mapDispatchToProps = (dispatch, props) => ({
  setActiveStep (step) {
    dispatch(setActiveStep(step))
  },
  save () {
    dispatch(statificationsSave())
  },
  pushToProd (sha) {
    dispatch(statificationsPushToProd(sha))
  },
  showDialog: (isOpen) => {
    dispatch(setDialogOpen(isOpen))
  },
  setDialogTitle: (title) => {
    dispatch(setDialogTitle(title))
  },
  setDialogText: (text) => {
    dispatch(setDialogText(text))
  },
  setDialogTypeAction: (typeAction) => {
    dispatch(setDialogTypeAction(typeAction))
  },
  clearForm: () => {
    dispatch(newForm())
  }
})

const StatificationCreateContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(StatificationCreate)

export default StatificationCreateContainer
