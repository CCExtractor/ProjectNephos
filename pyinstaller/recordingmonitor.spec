# -*- mode: python -*-

block_cipher = None


a = Analysis(
	['recordingmonitor.py'],
	pathex=['pyinstaller'],
	binaries=[],
	datas=[],
	hiddenimports=[
		'coloredlogs',
		'unav.recordingmonitor.jobs.maintenance',
		'unav.recordingmonitor.jobs.maintenance.free_space',
		'unav.recordingmonitor.jobs.maintenance.channel_on_air',
		'unav.recordingmonitor.jobs.templates.scripttpl',
	],
	hookspath=[],
	runtime_hooks=[],
	excludes=[],
	win_no_prefer_redirects=False,
	win_private_assemblies=False,
	cipher=block_cipher
)

pyz = PYZ(
	a.pure,
	a.zipped_data,
	cipher=block_cipher
)

options = [
	# ('v', None, 'OPTION'),
]

exe = EXE(
	pyz,
	a.scripts,
	options,
	exclude_binaries=True,
	name='recordingmonitor',
	debug=False,
	strip=False,
	upx=True,
	console=True
)

coll = COLLECT(
	exe,
	a.binaries,
	a.zipfiles,
	a.datas,
	strip=False,
	upx=True,
	name='recordingmonitor'
)
