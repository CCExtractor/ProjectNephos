// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import BootstrapVue from 'bootstrap-vue'
import VeeValidate from 'vee-validate'
import App from './App'
import store from './store'
import router from './router'
import { sync } from 'vuex-router-sync'
import VuesticPlugin from 'src/components/vuestic-components/vuestic-components-plugin'

import 'element-ui/lib/theme-default/index.css'
import ElementUI from 'element-ui'
import locale from 'element-ui/lib/locale/lang/en'
Vue.use(ElementUI, { locale })

Vue.use(VuesticPlugin)
Vue.use(BootstrapVue)

// NOTE: workaround for VeeValidate + vuetable-2
Vue.use(VeeValidate, {fieldsBagName: 'formFields'})

sync(store, router)

const mediaHandler = () => {
	if (window.matchMedia(store.getters.config.windowMatchSizeLg).matches) {
		store.dispatch('toggleSidebar', true)
	} else {
		store.dispatch('toggleSidebar', false)
	}
}

router.beforeEach((_unused_to, _unused_from, next) => {
	store.commit('setLoading', true)
	next()
})

router.afterEach((/*to, from*/) => {
	mediaHandler()
	store.commit('setLoading', false)
})

/* eslint-disable no-new */
new Vue({
	el: '#app',
	router,
	store,
	template: '<App/>',
	components: { App }
})
