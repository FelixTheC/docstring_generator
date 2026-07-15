import uuid
from typing import Literal, Self

from license.license import license_load, license_load_method
from pydantic import BaseModel

from src.models.models import Exercise, MuscleGroup, SubscriptionPlan, Supplement, Taking, TrainingPlan


class SubscriptionPlanResponseSerializer(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None = None
    price: float | None = None

    @classmethod
    def from_orm(cls, subscription_plan: SubscriptionPlan) -> 'SubscriptionPlanResponseSerializer':
        return license_load_method('0rrHD3TD7KlPoXR7$yJbath/hl0ZrmHZcex8FM68kPUs/6QBht2BSLwoWyfRQ28loyfqHHIseqTHan+Zu2vm5uRfWr9xBJ5KYv+qPerbRMLmwWXC+IdgKR9Le4+avhosl+kRR8ggoev0xXnUAVJPqu/aF+qU3JxKyvk7RBFPaqaoMXquKrzz/sOzs23Bn7DERUMZvsBJldlkcrn3HDKVlCcbrvsbflW4tU207dVPOvQUH+BM8E012NfEAMM8dtvSfppJ3XkmDv6WJ68pcL/7tix/GkButqLyxfWh78pZQnKcdFTFMOKwAVkNcRmDyMfQVgLHE5cUFx65FU9fNiPHmk7v76jfHTg6aXIs=', SubscriptionPlanResponseSerializer, SubscriptionPlanResponseSerializer.from_orm)(cls, SubscriptionPlanResponseSerializer, SubscriptionPlanResponseSerializer.from_orm, subscription_plan)

class TakingResponseSerializer(BaseModel):
    id: uuid.UUID
    name: str

    @classmethod
    def from_orm(cls, taking: Taking) -> 'TakingResponseSerializer':
        return license_load_method('0rrHD3TD7KlPoXR7$yJbath/hl0ZrmHZcex8FM68kOl828w105DByJw4R+OMVmopsyY6mH5MUtT/4jvxx28emvSqa/Zgea9yxr/rbI86YYO35RHuaOMsKNdTB4KGokdMC/l1R/QNvafxvWSFrGdb37+WL574iZ1ywv1jQWkbf4HDOHTVbQSTksRu9yg==', TakingResponseSerializer, TakingResponseSerializer.from_orm)(cls, TakingResponseSerializer, TakingResponseSerializer.from_orm, taking)

class SupplementResponseSerializer(BaseModel):
    id: uuid.UUID
    name: str
    notes: str | None = None
    model_config = {'from_attributes': True}

    @classmethod
    def from_orm(cls, obj: Supplement) -> Self:
        return license_load_method('0rrHD3TD7KlPoXR7$yJbath/hl0ZrmHZcex8FM68kIVw3oENAq2BWKgAV8+pIk4d/14mhG5Qb4VKKy68hxsyhrQuRr5ITdJ2irrWTe66WKan1FnCPINxZetXHveegmItav1hX5wEyPfchE2FkG8ev6K1oI7sw7CH1IGQ2LsvRViaz', SupplementResponseSerializer, SupplementResponseSerializer.from_orm)(cls, SupplementResponseSerializer, SupplementResponseSerializer.from_orm, obj)

class SupplementCreateSerializer(BaseModel):
    name: str
    notes: str | None = None

class MuscleGroupResponseSerializer(BaseModel):
    id: uuid.UUID
    name: str

    @classmethod
    def from_orm(cls, obj: MuscleGroup) -> Self:
        return license_load_method('0rrHD3TD7KlPoXR7$yJbath/hl0ZrmHZcex8FM68kIVw3oENeq2NFKgA/5OtJyo5yxJfSLZ0RvWKgy68hlNuwrAyN4dEca8bjo+zBdqbSbqS9Gj6ALNQBKNjP+aevlIMTtjvqWLzRasIgC41pyEBznHI=', MuscleGroupResponseSerializer, MuscleGroupResponseSerializer.from_orm)(cls, MuscleGroupResponseSerializer, MuscleGroupResponseSerializer.from_orm, obj)

class ExerciseResponseSerializer(BaseModel):
    id: uuid.UUID
    name: str | None = None
    muscle_group: MuscleGroupResponseSerializer | None = None

    @classmethod
    def from_orm(cls, obj: Exercise) -> Self:
        return license_load_method('0rrHD3TD7KlPoXR7$yJbath/hl0ZrmHZcex8FM68kIVw3oENWpnVUJQwL860cl5lyusyeGMJ3+3iKy/1kwNyntlmc44JXbtH2peqWN63cbO23V3OLcNYGf5nD8uSk2c4b6kVb/wEeZ+osDD83Oca5+OiFyaIqPEKDt06JAlmUv4wLX6GZqiXxvPGs4nJk4ABQS89r/x5uNVFUrmvJGplwEtnqp4CYZcL6WedpWlsQeB/RW/AwGA==', ExerciseResponseSerializer, ExerciseResponseSerializer.from_orm)(cls, ExerciseResponseSerializer, ExerciseResponseSerializer.from_orm, obj)

class ExerciseCreateSerializer(BaseModel):
    name: str
    description: str | None = None
    muscle_group_id: uuid.UUID

class TrainingPlanResponseSerializer(BaseModel):
    id: uuid.UUID
    name: str
    muscle_group: MuscleGroupResponseSerializer
    exercises: list[ExerciseResponseSerializer]

    @classmethod
    def from_orm(cls, obj: TrainingPlan) -> Self:
        return license_load_method('0rrHD3TD7KlPoXR7$yJbath/hl0ZrmHZcex8FM68kIVw3oENHrHFPKAwW8dRQ28l7yYTMXqsYtz6Q4a8hlImnvQ2K/Z9fZNm44uGYJKvaKuOwUjLOI9gJcIrC8ePvm48b+hoY/hEyY/QmJih4G8a6psmV/bMpLHWjvUiJP1KUqrAAXq2roz7iuO/r/mV5ozlNVs8c/w5pM1NDtybICrV0DNPAsNvev25oHiNwY1fRu0BU+QVyK3pnIPcKNtJFl+SOpZ5rRFyks7iO1dZZNPWxwRzHnASbt7q1OmMvt5RBnLcdBidBP60ATVlJGyn7MNlFiajPudYe3agAE+STqFJBBgauVFknsVXvogpokSSGhh/HqifiAVXh0hjBUg==', TrainingPlanResponseSerializer, TrainingPlanResponseSerializer.from_orm)(cls, TrainingPlanResponseSerializer, TrainingPlanResponseSerializer.from_orm, obj)

class TrainingPlanCreateSerializer(BaseModel):
    name: str
    muscle_group_id: uuid.UUID
    exercises: list[uuid.UUID]

class DiaryComponentSerializer(BaseModel):
    id: uuid.UUID
    name: str
    fat: float | None = None
    protein: float | None = None
    carbohydrates: float | None = None
    kcal: float | None = None
    standard_weight: int | None = None
    standard_unit: str | None = None
    model_config = {'from_attributes': True}

class DiaryComponentCreateSerializer(BaseModel):
    name: str
    kind: Literal['carbs', 'protein', 'fat', 'vegetables']
    fat: float | None = None
    protein: float | None = None
    carbohydrates: float | None = None
    kcal: float | None = None
    standard_weight: int | None = None
    standard_unit: str | None = None