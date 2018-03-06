<template>
	<div class="schedule">
		<div class="row">
			<div class="col-md-12">
				<vuestic-widget headerText="Create Job">
					<div class="row">
						<div class="col-sm-6 d-flex">

							<button
								class="btn btn-primary btn-with-icon"
								@click="showCreateJobModal()"
								>

								<div class="btn-with-icon-content">
									<i class="fa-plus fa"></i>
									Add Job
								</div>
							</button>
						</div>
					</div>
				</vuestic-widget>

 				<create-job ref="createJobModal" @create="createNewJob"></create-job>
			</div>
		</div>

		<div class="row">
			<div class="col-md-12">
				<vuestic-widget headerText="Scheduled Jobs">
					<vuestic-data-table
						:apiUrl="job_meta.apiUrl"
						:tableFields="job_meta.tableFields"
						:itemsPerPage="job_meta.itemsPerPage"
						:sortFunctions="job_meta.sortFunctions"
						:apiMode="job_meta.apiMode"
						:paginationPath="job_meta.paginationPath"
						:perPageInitial="10">
					</vuestic-data-table>
				</vuestic-widget>
			</div>
		</div>
	</div>
</template>

<script>
	import Vue from 'vue'

	import FieldsDef from './jobs-table/fields-definition'
	import ItemsPerPageDef from './jobs-table/items-per-page-definition'

	import CreateJob from './CreateJob'
	import StateColumn from './jobs-table/StateColumn'
	//import axios from 'axios'

	Vue.component('state-column', StateColumn)

	export default {
		name: 'schedule',
		components: {
			CreateJob,
			StateColumn,
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
			const apiRoot = this.$store.state.app.config.apiRoot

			return {
				job_meta: {
					apiUrl: `${apiRoot}/jobs`,
					apiMode: true,
					tableFields: FieldsDef.tableFields,
					itemsPerPage: ItemsPerPageDef.itemsPerPage,
					sortFunctions: FieldsDef.sortFunctions,
					paginationPath: ''
				}
			}
		},
		methods: {
			clear (field) {
				this[field] = ''
			},
			showCreateJobModal () {
				this.$refs.createJobModal.open()
			},
			createNewJob(job_info) {
				console.log(job_info)
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
