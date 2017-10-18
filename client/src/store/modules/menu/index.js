import * as types from '../../mutation-types'
import dashboard from './dashboard'
import schedule from './schedule'
import auth from './auth'

const state = {
	items: [
		dashboard,
		schedule,
		auth
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
