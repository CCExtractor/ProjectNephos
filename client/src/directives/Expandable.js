const directive = {
	dom: null,
	scrollbarTransition: {
		el: null,
		handler: null
	},
	inserted: (_unused_el, binding) => {
		const items = binding.value.menuItems
		const scrollbar = binding.value.refs.Scrollbar
		const childClassName = binding.value.childClassName
		const childHeight = binding.value.childHeight
		directive.dom = {
			elements: document.getElementsByClassName(childClassName),
			handlers: []
		}
		const parentId = binding.value.parentId
		directive.scrollbarTransition.el = document.getElementById(parentId).getElementsByClassName('vue-scrollbar-transition')[0]

		directive.scrollbarTransition.handler = _unused_event => {
			scrollbar.calculateSize()
		}

		directive.scrollbarTransition.el.addEventListener('transitionend', directive.scrollbarTransition.handler)

		const expandHandler = item => {
			return _unused_event => {
				if (!item.meta.expanded) {
					scrollbar.scrollToY(scrollbar.top - childHeight * item.children.length)
				} else {
					scrollbar.scrollToY(scrollbar.top + childHeight)
				}
				scrollbar.calculateSize()
			}
		}

		for (let i = 0; i < items.length; i++) {
			const item = items[i]
			const domItem = directive.dom.elements[i]
			directive.dom.handlers.push(expandHandler(item))
			if (item.children) {
				domItem.addEventListener('transitionend', directive.dom.handlers[i])
			}
		}
	},
	unbind: () => {
		directive.scrollbarTransition.el.removeEventListener('transitionend', directive.scrollbarTransition.handler)

		for (let i = 0; i < directive.dom.elements.length; i++) {
			directive.dom.elements[i].removeEventListener('transitionend', directive.dom.handlers[i])
		}
	}
}

module.exports = directive
