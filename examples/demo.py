"""Synthetic teaching fixture. No model, network, persistence or private records."""
from dataclasses import dataclass
from hashlib import sha256
import unittest


def digest(text):
    return sha256(text.encode('utf-8')).hexdigest()


@dataclass(frozen=True)
class Source:
    version: int
    project: str
    text: str
    accepted: bool = True


@dataclass(frozen=True)
class Result:
    source_version: int
    project: str
    text: str
    artifact_hash: str


def retrieve(source, result, project):
    if not source.accepted:
        return None
    if source.project != project or result.project != project:
        return None
    if source.version != result.source_version:
        return None
    if digest(result.text) != result.artifact_hash:
        return None
    return result.text


class ContractExamples(unittest.TestCase):
    def setUp(self):
        self.source = Source(1, 'synthetic-equipment', 'No unresolved faults')
        self.result = Result(1, self.source.project, 'No unresolved faults', digest('No unresolved faults'))

    def test_current_result(self):
        self.assertEqual(retrieve(self.source, self.result, self.source.project), 'No unresolved faults')

    def test_corrected_source_invalidates_old_result(self):
        updated = Source(2, self.source.project, 'One unresolved fault')
        self.assertIsNone(retrieve(updated, self.result, updated.project))

    def test_other_project_cannot_reuse(self):
        self.assertIsNone(retrieve(self.source, self.result, 'another-project'))

    def test_candidate_is_not_accepted_evidence(self):
        candidate = Source(1, self.source.project, self.source.text, False)
        self.assertIsNone(retrieve(candidate, self.result, candidate.project))

    def test_modified_artifact_is_rejected(self):
        modified = Result(1, self.source.project, 'Changed content', self.result.artifact_hash)
        self.assertIsNone(retrieve(self.source, modified, self.source.project))


if __name__ == '__main__':
    unittest.main(verbosity=2)
