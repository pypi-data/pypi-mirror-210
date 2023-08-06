import pytest
from typing import List
from torch.utils.data import Dataset, TensorDataset
import torch
from torchcross.data import TaskDescription, Task, TaskTarget
from torchcross.data.metadataset import CollectionMetaDataset  # replace with actual import


def create_task() -> Task:
    return Task(
        create_dataset(),
        create_dataset(),
        TaskTarget.MULTICLASS_CLASSIFICATION,
        {0: "a", 1: "b", 2: "c"},
    )


def create_dataset() -> Dataset:
    return TensorDataset(torch.rand(10), torch.randint(0, 3, (10,)))


def create_task_description() -> TaskDescription:
    return TaskDescription(
        TaskTarget.MULTICLASS_CLASSIFICATION,
        {0: "a", 1: "b"},
        "test",
    )


class TestCollectionMetaDataset:
    @pytest.fixture
    def tasks(self) -> List[Task]:
        return [create_task() for _ in range(5)]

    @pytest.fixture
    def datasets(self) -> List[Dataset]:
        return [create_dataset() for _ in range(5)]

    @pytest.fixture
    def task_descriptions(self) -> List[TaskDescription]:
        return [create_task_description() for _ in range(5)]

    def test_init_with_tasks(self, tasks):
        dataset = CollectionMetaDataset(tasks)
        assert dataset.tasks == tasks

    def test_init_with_datasets_and_descriptions(self, datasets, task_descriptions):
        dataset = CollectionMetaDataset(datasets, datasets, task_descriptions)
        assert len(dataset.tasks) == len(datasets)
        for task, dataset, task_description in zip(
            dataset.tasks, datasets, task_descriptions
        ):
            assert task.support == dataset
            assert task.query == dataset
            assert task.task_target == task_description.task_target
            assert task.classes == task_description.classes

    def test_init_with_invalid_arguments(self, tasks, datasets):
        with pytest.raises(TypeError):
            CollectionMetaDataset(tasks, datasets, datasets)

    def test_init_with_no_arguments(self):
        with pytest.raises(TypeError):
            CollectionMetaDataset()

    def test_tasks_property(self, tasks):
        dataset = CollectionMetaDataset(tasks)
        assert dataset.tasks == tasks
