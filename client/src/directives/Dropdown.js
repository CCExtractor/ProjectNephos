export default {
	bind: function (el, binding) {
		const ddToggle = el.querySelector('.dropdown-toggle')
		const ddMenu = el.querySelector('.dropdown-menu')
		const closeOnMenuClick = binding.modifiers.closeOnMenuClick

		ddToggle.addEventListener('click', function (evt) {
			evt.preventDefault()
			const isShown = el.classList.contains('show')
			setTimeout(() => el.classList.toggle('show', !isShown))
		})

		window.addEventListener('click', function () {
			el.classList.remove('show')
		})

		ddMenu.addEventListener('click', function (evt) {
			if (!closeOnMenuClick) {
				evt.stopPropagation()
			}
		})
	}
}
