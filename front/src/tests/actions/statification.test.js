import * as actions from '../../actions/statifications.js'
import * as types from '../../constants/ActionTypes.js'

describe('Statification reducer actions', () => {
  it('should create an action to clear the setInterval', () => {
    const actionClearIntervalFalse = {
      type: types.STATIFICATION_CLEAR_INTERVAL,
      clearInterval: false
    }

    const actionClearIntervalTrue = {
      type: types.STATIFICATION_CLEAR_INTERVAL,
      clearInterval: true
    }

    expect(actions.setClearInterval()).toEqual(actionClearIntervalFalse)
    expect(actions.setClearInterval(true)).toEqual(actionClearIntervalTrue)
  })
})
