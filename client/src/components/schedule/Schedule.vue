<template>
	<div class="schedule">
		<div class="row">
			<div class="col-md-12">
				<vuestic-widget headerText="Create Job">
					<div class="row">
						<div class="col-sm-6 d-flex justify-content-center">

							<button
								class="btn btn-primary btn-with-icon rounded-icon"
								@click="showCreateJobModal()"
								>


								<div class="btn-with-icon-content">
									<i class="entypo entypo-plus"></i>
								</div>
							</button>
						</div>
					</div>
				</vuestic-widget>
<!-- 				<modal :show.sync="show" v-bind:large="true" ref="createJobModal" @ok="asdf">
					<div slot="title">Create new Job</div>
					<div>
						<div>
							Start at
							<el-date-picker
								v-model="date_from"
								type="datetime"
								placeholder="Select date and time">
							</el-date-picker>
						</div>

						<div>
							Stop at
							<el-date-picker
								v-model="date_trim"
								type="datetime"
								placeholder="Select date and time">
							</el-date-picker>
						</div>

					</div>
				</modal>
 -->
 				<create-job ref="createJobModal" @create="asdf"></create-job>
			</div>
		</div>
	</div>
</template>

<script>
	import VuesticSwitch from '../../components/vuestic-components/vuestic-switch/VuesticSwitch'
	import VuesticSimpleSelect from '../../components/vuestic-components/vuestic-simple-select/VuesticSimpleSelect'
	import VuesticMultiSelect from '../../components/vuestic-components/vuestic-multi-select/VuesticMultiSelect'
	import Widget from '../../components/vuestic-components/vuestic-widget/VuesticWidget'
	import Modal from '../../components/vuestic-components/vuestic-modal/VuesticModal'

	import CreateJob from './CreateJob'
	//import axios from 'axios'

	export default {
		name: 'schedule',
		components: {
			VuesticSwitch,
			VuesticSimpleSelect,
			VuesticMultiSelect,
			Widget,
			Modal,
			CreateJob,
		},
		computed: {
			isSuccessfulEmailValid () {
				let isValid = false
				if (this.formFields.successfulEmail) {
					isValid = this.formFields.successfulEmail.validated && this.formFields.successfulEmail.valid
				}
				return isValid
			}
		},
		data () {
			return {
			}
		},
		methods: {
			clear (field) {
				this[field] = ''
			},
			showCreateJobModal () {
				this.$refs.createJobModal.open()
			},
			asdf(xx) {
				console.log(xx)
			}
		},
		mounted () {
			this.$validator.validateAll()
		}
	}
</script>

<style lang="scss">
	.abc-checkbox, .abc-radio {
		display: flex !important;
		justify-content: flex-start;
	}

	input[type=checkbox]:disabled + label, input[type=radio]:disabled + label,
	input[type=checkbox]:disabled, input[type=radio]:disabled {
		cursor: not-allowed;
	}
</style>
