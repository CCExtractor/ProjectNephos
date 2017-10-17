<template>
	<modal :show.sync="show" v-bind:large="true" ref="mainModal" @ok="create">
		<div slot="title">Create new Job</div>

		<form>

			<div class="row">
				<div class="col-md-12">
					<fieldset>
						<div class="form-group">
 							<div class="input-group">
								<el-date-picker
									id="simple-input"
									v-model="date_from"
									type="datetime"
									placeholder="Select date and time">
								</el-date-picker>
							</div>
						</div>
						<div class="form-group">
							<div class="input-group">
								<input id="inputWithDescription" required title=""/>
								<label class="control-label" for="simple-input">Text input (with description)</label><i
								class="bar"></i>
								<small class="help text-secondary">
									Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
									tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
									quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
									consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
									cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
									proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
								</small>
							</div>
						</div>

						<div>
							Stop at
							<el-date-picker
								v-model="date_trim"
								type="datetime"
								placeholder="Select date and time">
							</el-date-picker>
						</div>

					</fieldset>

				</div>
			</div>
		</form>

	</modal>

</template>

<script>
	import VuesticSwitch from '../../components/vuestic-components/vuestic-switch/VuesticSwitch'
	import VuesticSimpleSelect from '../../components/vuestic-components/vuestic-simple-select/VuesticSimpleSelect'
	import VuesticMultiSelect from '../../components/vuestic-components/vuestic-multi-select/VuesticMultiSelect'
	import Modal from '../../components/vuestic-components/vuestic-modal/VuesticModal'

	import moment from 'moment'

	export default {
		name: 'create-job',
		components: {
			VuesticSwitch,
			VuesticSimpleSelect,
			VuesticMultiSelect,
			Modal,
		},
		data () {
			return {
				date_from: new Date(),
				date_trim: moment().add(2, 'hours'),

				show: true,
			}
		},
		methods: {
			clear (field) {
				this[field] = ''
			},
			open () {
				this.$refs.mainModal.open()
			},
			create() {
				this.$emit('create', this.$data)
			}
		},
		mounted () {
			this.$validator.validateAll()
		}
	}
</script>
