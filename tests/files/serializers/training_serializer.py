import datetime as dt
import uuid

from pydantic import BaseModel, ConfigDict

from .utilities_serializer import ExerciseResponseSerializer, MuscleGroupResponseSerializer


class ExerciseReadSerializer(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None = None
    muscle_group: MuscleGroupResponseSerializer
    model_config = ConfigDict(from_attributes=True)

class ExerciseUpdateSerializer(BaseModel):
    name: str | None = None
    description: str | None = None
    muscle_group_id: uuid.UUID | None = None

class TrainingPlanReadSerializer(BaseModel):
    id: uuid.UUID
    name: str
    muscle_group: MuscleGroupResponseSerializer
    exercises: list[ExerciseResponseSerializer]
    model_config = ConfigDict(from_attributes=True)

class TrainingPlanUpdateSerializer(BaseModel):
    name: str | None = None
    muscle_group_id: uuid.UUID | None = None
    exercises: list[uuid.UUID] | None = None

class UserTrainingPlanExerciseUpdateSerializer(BaseModel):
    progression: int | None = None
    sets: int | None = None
    weight: float | None = None

class UserTrainingPlanReadSerializer(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    day: int
    training_plan: TrainingPlanReadSerializer | None = None
    user_training_plan_exercises: list['UserTrainingPlanExerciseReadSerializer']
    model_config = ConfigDict(from_attributes=True)

class UserTrainingPlanExerciseReadSerializer(BaseModel):
    id: uuid.UUID
    user_training_plan_id: uuid.UUID
    exercise_id: uuid.UUID
    progression: int
    sets: int
    exercise: ExerciseReadSerializer
    model_config = ConfigDict(from_attributes=True)

class UserTrainingPlanUpdateSerializer(BaseModel):
    day: int | None = None
    training_plan_id: uuid.UUID | None = None

class UserTrainingsPlanExerciseUpdateSerializer(BaseModel):
    exercise_id: uuid.UUID
    progression: int | None = None
    sets: int | None = None
    weight: int | None = None

class UserTrainingsPlanUpdateSerializer(BaseModel):
    trainings_plan: TrainingPlanReadSerializer | None = None
    user_exercise: UserTrainingsPlanExerciseUpdateSerializer | None = None

class UserTrainingExerciseReadExerciseSerializer(BaseModel):
    id: uuid.UUID
    user_training_id: uuid.UUID
    exercise: ExerciseReadSerializer
    weight: float | None = None
    sets: int | None = None
    model_config = ConfigDict(from_attributes=True)

class UserTrainingReadSerializer(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: dt.datetime
    updated_at: dt.datetime
    training_plan: UserTrainingPlanReadSerializer | None = None
    exercises: list[UserTrainingExerciseReadExerciseSerializer]
    model_config = ConfigDict(from_attributes=True)

class UserTrainingUpdateSerializer(BaseModel):
    weight: float | None = None
    sets: int | None = None

class UserTrainingPerformanceReadSerializer(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    user_training_plan_id: uuid.UUID
    weight: float | None = None
    reps: int | None = None
    set: int | None = None
    exercise: ExerciseReadSerializer

class UserTrainingPerformanceCreateSerializer(BaseModel):
    user_id: uuid.UUID
    user_training_plan_id: uuid.UUID
    exercise_id: uuid.UUID
    weight: float | None = None
    reps: int | None = None
    set: int | None = None

class UserTrainingPerformanceUpdateSerializer(BaseModel):
    weight: float | None = None
    reps: int | None = None
    set: int