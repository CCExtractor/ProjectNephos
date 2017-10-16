import store from 'store'

export default {
	inserted: function (el) {
		const getWindowMatch = () => {
			return window.matchMedia(store.getters.config.windowMatchSizeLg).matches
		}

		let prevMatchlg = getWindowMatch()

		el.addEventListener('transitionend', function () {
			store.dispatch('isToggleWithoutAnimation', false)
		})

		window.addEventListener('resize', function () {
			if (getWindowMatch() && !prevMatchlg) {
				store.dispatch('toggleSidebar', true)
			} else if (!getWindowMatch() && prevMatchlg) {
				store.dispatch('isToggleWithoutAnimation', true)
				store.dispatch('toggleSidebar', false)
			}
			prevMatchlg = getWindowMatch()
		})
	}
}

