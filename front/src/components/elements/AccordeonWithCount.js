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
import React from 'react'
import PropTypes from 'prop-types'
import { Card, CardContent, CardActions, IconButton, Collapse } from '@material-ui/core'
import { ExpandMore } from '@material-ui/icons'
import CountElement from './CountElement'

export default class AccordeonWithCount extends React.PureComponent {
  constructor (props) {
    super(props)
    this.handleClick = this.handleClick.bind(this)
  }

  handleClick (e) {
    if (this.props.onAccordeonChange && typeof (this.props.onAccordeonChange) === 'function') { this.props.onAccordeonChange(this.props.accordeon) }
  }

  render () {
    return (
      <Card>
        <CardActions onClick={this.handleClick} className={`${this.props.open ? 'accordeon_open' : 'accordeon_closed'} accordeon'`}>
          <div className='collapse_title'>
            <div>{this.props.title}</div>
            <div><CountElement count={this.props.count} level={this.props.level} /></div>
          </div>
          <div className='collapse_grow' />
          <IconButton className={this.props.open ? 'collapse_open' : 'collapse_closed'} onClick={this.handleClick}>
            <ExpandMore />
          </IconButton>
        </CardActions>
        <Collapse in={this.props.open}>
          <CardContent>
            {this.props.children}
          </CardContent>
        </Collapse>
      </Card>
    )
  }
}

/**
 * Define default value for the component
 * @type {Object}
 */
AccordeonWithCount.defaultProps = {
  open: false,
  onAccordeonChange: undefined,
  accordeon: ''
}

/**
 * Define the types of properties for the component
 * @type {Object}
 */
AccordeonWithCount.propTypes = {
  title: PropTypes.string.isRequired,
  children: PropTypes.instanceOf(Object).isRequired,
  count: PropTypes.number.isRequired,
  level: PropTypes.string.isRequired,
  open: PropTypes.bool,
  onAccordeonChange: PropTypes.func,
  accordeon: PropTypes.string
}
