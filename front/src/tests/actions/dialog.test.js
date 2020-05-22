import * as actions from '../../actions/dialog.js'
import * as types from '../../constants/ActionTypes.js'

describe('Dialog reducer actions', () => {
  it('should create an action to open the dialog', () => {
    const actionTrue = {
      type: types.DIALOG_SET_OPEN,
      open: true
    }

    const actionFalse = {
      type: types.DIALOG_SET_OPEN,
      open: false
    }

    expect(actions.setDialogOpen(true)).toEqual(actionTrue)
    expect(actions.setDialogOpen(false)).toEqual(actionFalse)
  })
})
