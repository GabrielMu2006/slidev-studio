import test from 'node:test'
import assert from 'node:assert/strict'
import { access } from 'node:fs/promises'
import { join } from 'node:path'
import { apply, inject } from '../adapters/dsh/index.mjs'

test('DSH provider exposes both skills with runnable local resources', async () => {
  let provider
  apply({ skills: { registerProvider(factory) { provider = factory({}) } } })
  assert.deepEqual(inject, ['skills'])
  const candidates = await provider.list()
  assert.deepEqual(candidates.map(row => row.name), ['slidev', 'slidev-template-import'])
  for (const row of candidates) {
    assert.equal(row.provider, 'slidev-studio')
    assert.equal(row.source, 'bundled')
    assert.equal(row.invocation.modelInvocable, true)
    const body = await provider.get(row)
    assert.ok(body.content.trimStart().startsWith('# '))
    assert.ok(!body.content.startsWith('---'))
    assert.equal(body.resourceBase.kind, 'directory')
    await access(join(body.resourceBase.path, 'scripts', row.name === 'slidev' ? 'studio.py' : 'template_bundle.py'))
  }
  assert.equal(await provider.get({ locator: '../outside' }), undefined)
})
