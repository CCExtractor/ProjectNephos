export default {
	bind (_unused_el, binding, vnode) {
		const HORIZONTAL_LAYOUT = 'horizontal'
		const VERTICAL_LAYOUT = 'vertical'
		const initialLayout = binding.value.layout
		const breakpoint = binding.value.breakPoint

		let wizardLayout = initialLayout

		const handleResize = () => {
			const width = window.innerWidth
			const layout = width <= breakpoint ? HORIZONTAL_LAYOUT : VERTICAL_LAYOUT
			if (wizardLayout !== layout) {
				wizardLayout = layout
				vnode.context.$emit('wizardLayoutChange', wizardLayout)
			}
		}

		if (initialLayout === VERTICAL_LAYOUT) {
			handleResize()
			window.addEventListener('resize', handleResize)
		}
	}
}
