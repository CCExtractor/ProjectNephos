<template>
	<vuestic-modal :show.sync="show" v-bind:large="true" ref="mainModal" @ok="create">
		<div slot="title">Create new Job</div>

		<form>

			<div class="row">
				<div class="col-md-12">
					<fieldset>
						<div class="form-group">
							<div class="input-group">
								<input v-model="job_info.name" id="job_name" required title=""/>
								<label class="control-label" for="job_name">
									Job Name
								</label>
								<i class="bar"></i>
								<small class="help text-secondary">Input a name for a new job
								</small>
							</div>
						</div>

						<div
						<div class="form-group">

  							<div class="input-group">

								<el-date-picker
									id="job_date_from"
									v-model="job_info.date_from"
									type="datetime"
									placeholder="Select date and time">
								</el-date-picker>

								<i class="bar"></i>
								<small class="help text-secondary">Start date/time
								</small>

 							</div>
						</div>

						<div class="form-group">

  							<div class="input-group">

								<el-date-picker
									id="job_date_from"
									v-model="job_info.date_trim"
									type="datetime"
									placeholder="Select date and time">
								</el-date-picker>

								<i class="bar"></i>
								<small class="help text-secondary">End date/time
								</small>
 							</div>
						</div>

					</fieldset>

				</div>
			</div>
		</form>

	</vuestic-modal>

</template>

<script>
	import moment from 'moment'
	import _ from 'lodash'

	export default {
		name: 'create-job',
		components: {
		},
		data () {
			const initDate = moment().startOf('hour')
			return {
				job_info: {
					name: '',
					date_from: initDate.toDate(),
					date_trim: initDate.clone().add(2, 'h').toDate(),
				},

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
				const d = _.pick(this.$data.job_info, [
					'name',
					'date_from',
					'date_trim',
				])
				this.$emit('create', d)
			}
		},
		mounted () {
			this.$validator.validateAll()
		}
	}
</script>
