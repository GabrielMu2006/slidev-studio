import { readFile } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'

export const name = 'slidev-studio'
export const inject = ['skills']
const root = new URL('../../plugins/slidev-studio/', import.meta.url)
const names = ['slidev', 'slidev-template-import']
const invocation = { modelInvocable: true, userInvocable: true }

async function definition(skillName) {
  const directory = new URL(`skills/${skillName}/`, root)
  const file = new URL('SKILL.md', directory)
  const raw = await readFile(file, 'utf8')
  const match = /^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/.exec(raw)
  if (!match) throw new Error(`Missing skill frontmatter: ${skillName}`)
  const field = key => new RegExp(`^${key}: (.+)$`, 'm').exec(match[1])?.[1]?.trim()
  if (field('name') !== skillName || !field('description')) throw new Error(`Invalid skill metadata: ${skillName}`)
  return { name: skillName, description: field('description'), invocation,
    provider: name, source: 'bundled', path: fileURLToPath(file),
    resourceBase: { kind: 'directory', path: fileURLToPath(directory) }, content: match[2] }
}

export function apply(ctx) {
  ctx.skills.registerProvider(() => ({
    name,
    async list() {
      return Promise.all(names.map(async skillName => {
        const { content, ...summary } = await definition(skillName)
        return { ...summary, rank: 600, locator: skillName }
      }))
    },
    async get(candidate) {
      return names.includes(candidate.locator) ? definition(candidate.locator) : undefined
    },
  }))
}
