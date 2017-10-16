import * as types from '../../mutation-types'
import statistics from './statistics'
import forms from './forms'
import dashboard from './dashboard'
import ui from './ui'
import schedule from './schedule'
import tables from './tables'
import auth from './auth'
import extra from './extra'

const state = {
	items: [
		dashboard,
		schedule,
		statistics,
		forms,
		tables,
		ui,
		extra,
		auth
		// maps
	]
}

const mutations = {
	[types.TOGGLE_EXPAND_MENU_ITEM] (_unused_state, payload) {
		const menuItem = payload.menuItem
		const expand = payload.expand
		if (menuItem.children && menuItem.meta) {
			menuItem.meta.expanded = expand
		}
	}
}

const actions = {
	toggleExpandMenuItem ({commit}, payload) {
		commit(types.TOGGLE_EXPAND_MENU_ITEM, payload)
	}
}

export default {
	state,
	mutations,
	actions
}
