import * as actions from '../../actions/errors.js'
import * as types from '../../constants/ActionTypes.js'

describe('Error reducer actions', () => {
  it('should create an action to push a new Error', () => {
    const actionError = {
      type: types.ERROR_PUSH,
      message: 'test',
      severity: 'error'
    }

    const actionWarn = {
      type: types.ERROR_PUSH,
      message: 'test',
      severity: 'warn'
    }

    expect(actions.pushError('test', 'error' )).toEqual(actionError)
    expect(actions.pushError('test', 'warn')).toEqual(actionWarn)
  })
})
