from __future__ import annotations

import argparse
import importlib
import uuid
from datetime import datetime, UTC
from typing import Generator, List, Optional, Union, Annotated, Sequence

import jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from files import crud
from files.connection import get_async_db
from files.models import TrainingPlan, Exercise, BaseModel
from files.serializers.training_serializer import TrainingPlanReadSerializer, TrainingPlanUpdateSerializer, \
    ExerciseReadSerializer, ExerciseUpdateSerializer
from files.serializers.utilities_serializer import TrainingPlanResponseSerializer


# =====================================================================
# PART 0: Custom Exception Hierarchy
# =====================================================================

class AppError(Exception):
    """Base exception for all application-level errors."""


class ValidationError(AppError):
    """Raised when input data fails validation."""

    def __init__(self, field: str, message: str) -> None:
        """
        Args:
            field (str): 
            message (str): 
        Returns:
            None: 
        """
        self.field = field
        super().__init__(f"[{field}] {message}")


class NotFoundError(AppError):
    """Raised when a requested resource cannot be located."""

    def __init__(self, resource: str, identifier) -> None:
        """
        Args:
            resource (str): 
            identifier (Any): 
        Returns:
            None: 
        """
        self.resource = resource
        self.identifier = identifier
        super().__init__(f"{resource} with id={identifier!r} not found")


class PermissionDeniedError(AppError):
    """Raised when an operation is not permitted for the current user."""

    def __init__(self, action: str, user: str) -> None:
        """
        Args:
            action (str): 
            user (str): 
        Returns:
            None: 
        """
        self.action = action
        self.user = user
        super().__init__(f"User '{user}' is not allowed to perform '{action}'")


class RetryableError(AppError):
    """Transient error that the caller may retry after a delay."""

    def __init__(self, reason: str, retry_after: float = 1.0) -> None:
        """
        Args:
            reason (str): 
            retry_after (float, optional): Defaults to 1.0.
        Returns:
            None: 
        """
        self.retry_after = retry_after
        super().__init__(f"Transient failure: {reason} (retry after {retry_after}s)")


def empty_args_no_docstring():
    return None


def empty_args_with_docstring():
    """This function does nothing."""
    return None

# =====================================================================
# PART 1: Raising built-in exceptions – every common mechanism
# =====================================================================

def raise_value_error(value: int) -> int:
    """
    Validate that an integer is non-negative, otherwise raise an error.
    
    Args:
        value (int): 
    Returns:
        int: 
    Raises:
        ValueError: If value < 0
    """
    if value < 0:
        raise ValueError(f"Expected a non-negative integer, got {value}")
    return value


def raise_type_error(value) -> str:
    """
    Args:
        value (Any): 
    Returns:
        str: 
    Raises:
        TypeError: If not isinstance(value, str)
    """
    if not isinstance(value, str):
        raise TypeError(f"Expected str, got {type(value).__name__}")
    return value.upper()


def raise_index_error(data: list, *, index: int):
    """
    Args:
        data (list): 
        index (int): Keyword only argument. 
    Raises:
        IndexError: If index >= len(data) or index < -len(data)
    """
    if index >= len(data) or index < -len(data):
        raise IndexError(f"Index {index} is out of range for list of length {len(data)}")
    return data[index]


def raise_key_error(mapping: dict, key: str, /):
    """
    Args:
        mapping (dict): Positional only argument. 
        key (str): Positional only argument. 
    Raises:
        KeyError: If key not in mapping
    """
    if key not in mapping:
        raise KeyError(key)
    return mapping[key]


def raise_runtime_error(flag: bool) -> None:
    """
    Args:
        flag (bool): 
    Returns:
        None: 
    Raises:
        RuntimeError: If flag
    """
    if flag:
        raise RuntimeError("An unrecoverable runtime condition was detected")


def raise_not_implemented() -> None:
    """
    Returns:
        None: 
    Raises:
        NotImplementedError: If a certain condition is met.
    """
    raise NotImplementedError("This method has not been implemented yet")


def raise_attribute_error(obj) -> None:
    """
    Args:
        obj (Any): 
    Returns:
        None: 
    Raises:
        AttributeError: If not hasattr(obj, 'name')
    """
    if not hasattr(obj, "name"):
        raise AttributeError(f"Object of type {type(obj).__name__} has no attribute 'name'")


def raise_zero_division_error(divisor: float) -> float:
    """
    Args:
        divisor (float): 
    Returns:
        float: 
    Raises:
        ZeroDivisionError: If divisor == 0
    """
    if divisor == 0:
        raise ZeroDivisionError("Division by zero is not allowed")
    return 1.0 / divisor


def raise_overflow_error(exponent: int) -> int:
    """
    Args:
        exponent (int): 
    Returns:
        int: 
    Raises:
        OverflowError: If result > 2 ** 63 - 1
    """
    result = 2 ** exponent
    if result > 2 ** 63 - 1:
        raise OverflowError(f"Result 2**{exponent} exceeds 64-bit signed integer range")
    return result


def raise_stop_iteration() -> None:
    """
    Returns:
        None: 
    Raises:
        StopIteration: If a certain condition is met.
    """
    raise StopIteration("Iterator exhausted")


# =====================================================================
# PART 2: Re-raising and chained exceptions
# =====================================================================

def reraise_with_context(data: dict, key: str):
    """
    Args:
        data (dict): 
        key (str): 
    Raises:
        NotFoundError: Re-Raised from KeyError
    """
    try:
        return data[key]
    except KeyError as exc:
        raise NotFoundError("DictEntry", key) from exc


def suppress_and_raise_new(items: list, index: int):
    """
    Args:
        items (list): 
        index (int): 
    Raises:
        ValidationError: Re-Raised from IndexError
    """
    try:
        return items[index]
    except IndexError:
        raise ValidationError("index", f"Value {index} is out of bounds") from None


def reraise_bare(value: int) -> int:
    """
    Args:
        value (int): 
    Returns:
        int: 
    Raises:
        ValueError: Re-raising this handled exception
    """
    try:
        return raise_value_error(value)
    except ValueError:
        print("Logging: caught ValueError, re-raising")
        raise


# =====================================================================
# PART 3: Exceptions inside generators and context managers
# =====================================================================

def generator_with_exception(limit: int) -> Generator[int, None, None]:
    """
    Args:
        limit (int): 
    Returns:
        Generator[int | None | None]: 
    Raises:
        ValueError: If limit < 0
    """
    if limit < 0:
        raise ValueError(f"limit must be >= 0, got {limit}")
    for i in range(limit):
        yield i


def context_manager_raise(path: str):
    """
    Args:
        path (str): 
    Raises:
        FileNotFoundError: If not path
    """
    if not path:
        raise FileNotFoundError("Cannot open file: path is empty")
    with open(path) as fh:
        return fh.read()


# =====================================================================
# PART 4: Custom exception usage – all flavors
# =====================================================================

def validate_age(age: int) -> int:
    """
    Args:
        age (int): 
    Returns:
        int: 
    Raises:
        ValidationError: If age < 0 or age > 150
        ValidationError: If not isinstance(age, int)
    """
    if not isinstance(age, int):
        raise ValidationError("age", "must be an integer")
    if age < 0 or age > 150:
        raise ValidationError("age", f"value {age} is outside the range [0, 150]")
    return age


def find_user(users: dict, user_id: int) -> dict:
    """
    Args:
        users (dict): 
        user_id (int): 
    Returns:
        dict: 
    Raises:
        NotFoundError: If user_id not in users
    """
    if user_id not in users:
        raise NotFoundError("User", user_id)
    return users[user_id]


def perform_admin_action(user: str, is_admin: bool) -> str:
    """
    Args:
        user (str): 
        is_admin (bool): 
    Returns:
        str: 
    Raises:
        PermissionDeniedError: If not is_admin
    """
    if not is_admin:
        raise PermissionDeniedError("admin_action", user)
    return f"Action performed by {user}"


def connect_to_service(attempts: int) -> str:
    """
    Args:
        attempts (int): 
    Returns:
        str: 
    Raises:
        RetryableError: If attempts <= 0
    """
    if attempts <= 0:
        raise RetryableError("All connection attempts failed", retry_after=5.0)
    return "connected"


# =====================================================================
# PART 5: Exception groups / multi-exception catch
# =====================================================================

def parse_number(text: str) -> float:
    """
    Args:
        text (str): 
    Returns:
        float: 
    Raises:
        ValidationError: If a certain condition is met.
    """
    try:
        result = float(text)
    except (ValueError, OverflowError) as exc:
        raise ValidationError("text", f"cannot parse '{text}' as a number") from exc
    return result

def greet_user(name: str, greeting: str = "Hello", uppercase: bool = False) -> str:
    """
    Lorem ipsum dolor sit amet, consetetur sadipscing elitr,
    sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam
            
    Args:
        name (str): Lorem ipsum dolor sit amet. 
        greeting (str, optional): Defaults to 'Hello'.
        uppercase (bool, optional): nonumy eirmod tempor invidun. Defaults to False.
    Returns:
        str: 
    """
    message = f"{greeting}, {name}!"
    return message.upper() if uppercase else message

def safe_divide(a: Union[int, float], b: Union[int, float]) -> float:
    """
    Args:
        a (int | float): 
        b (int | float): 
    Returns:
        float: 
    Raises:
        ValidationError: Re-Raised from ZeroDivisionError
    """
    try:
        return a / b
    except ZeroDivisionError as exc:
        raise ValidationError("b", "denominator must not be zero") from exc


# =====================================================================
# PART 6: Raising inside comprehensions, lambdas, and nested functions
# =====================================================================

def filtered_sqrt(values: List[float]) -> List[float]:
    """
    Args:
        values (List[float]): 
    Returns:
        List[float]: 
    Raises:
        ValueError: If x < 0
    """
    def _sqrt(x: float) -> float:
        """
        Args:
            x (float): 
        Returns:
            float: 
        Raises:
            ValueError: If x < 0
        """
        if x < 0:
            raise ValueError(f"Cannot compute sqrt of negative number {x}")
        return x ** 0.5

    return [_sqrt(v) for v in values]


def make_multiplier(factor: float):
    """
    Args:
        factor (float): 
    """
    return lambda x: (
        x * factor
        if isinstance(x, (int, float))
        else (_ for _ in ()).throw(TypeError(f"Expected numeric, got {type(x).__name__}"))
    )


# =====================================================================
# PART 7: Fully Typed Class with Dunder and Custom Methods
# =====================================================================

class InventoryBatch:

    def __init__(self, batch_id: int, items: Optional[List[str]] = None) -> None:
        """
        Args:
            batch_id (int): 
            items (List[str] | None, optional): Defaults to None.
        Returns:
            None: 
        Raises:
            ValidationError: If not isinstance(batch_id, int) or batch_id < 0
        """
        if not isinstance(batch_id, int) or batch_id < 0:
            raise ValidationError("batch_id", "must be a non-negative integer")
        self.batch_id: int = batch_id
        self.items: List[str] = items if items is not None else []

    def __str__(self) -> str:
        """
        Returns:
            str: 
        """
        return f"Inventory Batch #{self.batch_id} containing {len(self.items)} items"

    def __repr__(self) -> str:
        """
        Returns:
            str: 
        """
        return f"InventoryBatch(batch_id={self.batch_id!r}, items={self.items!r})"

    def __len__(self) -> int:
        """
        Returns:
            int: 
        """
        return len(self.items)

    def __iter__(self) -> Generator[str, None, None]:
        """
        Returns:
            Generator[str | None | None]: 
        """
        for item in self.items:
            yield item

    def add_item(self, item_name: str) -> None:
        """
        Lorem ipsum dolor sit amet, consetetur sadipscing elitr,
        sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam
                
        Args:
            item_name (str): Lorem ipsum dolor sit amet. 
        Returns:
            None: 
        Raises:
            ValidationError: If not item_name.strip()
        """
        if not item_name.strip():
            raise ValidationError("item_name", "cannot be empty or just whitespace")
        self.items.append(item_name)

    def remove_item(self, item_name: str) -> str:
        """
        Args:
            item_name (str): 
        Returns:
            str: 
        Raises:
            NotFoundError: If item_name not in self.items
        """
        if item_name not in self.items:
            raise NotFoundError("Item", item_name)
        self.items.remove(item_name)
        return item_name

    def get_item(self, index: int) -> str:
        """
        Args:
            index (int): 
        Returns:
            str: 
        Raises:
            ValidationError: Re-Raised from IndexError
        """
        try:
            return self.items[index]
        except IndexError as exc:
            raise ValidationError(
                "index", f"{index} is out of range for batch of size {len(self.items)}"
            ) from exc

    @classmethod
    def new_batch(cls, elements: list[str]) -> "InventoryBatch":
        """
        Args:
            elements (list[str]): 
        Returns:
            'InventoryBatch': 
        """
        from random import randint
        batch = InventoryBatch(randint(1, 100))
        batch.items.extend(elements)
        return batch


class Command:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self._args = []

    @property
    def args(self):
        return self._args

    @args.setter
    def args(self, cl_args: list[str]):
        """
        Args:
            cl_args (list[str]): 
        """
        self._args = self.parser.parse_args(cl_args)

    def __call__(self, sys_args: list[str]):
        """
        Args:
            sys_args (list[str]): 
        """
        _, file_name, *kwargs = sys_args
        cls = "".join(obj.title() for obj in file_name.split("_"))
        obj = getattr(importlib.import_module(f"commands.{file_name}", cls), cls)()
        obj.add_arguments()
        obj.args = kwargs
        obj.handler()


# =====================================================================
# PART 8: Async functions
# =====================================================================
from fastapi import APIRouter, Depends, HTTPException
router = APIRouter(prefix="/training", tags=["training"])

oauth2_scheme = HTTPBearer()

def decode_jwt(val):
    """
    Args:
        val (Any): 
    """
    return object()

class UserAuth(BaseModel):
    user_id: uuid.UUID
    is_active: bool
    is_superuser: bool
    scopes: dict
    iat: datetime
    exp: datetime

async def get_current_user(token: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)]) -> UserAuth | None:
    """
    Args:
        token (HTTPAuthorizationCredentials): 
    Returns:
        UserAuth | None: 
    Raises:
        HTTPException: If a certain condition is met.
        HTTPException: If current_time > user_auth.exp
        HTTPException: If not user_auth.is_active
    """
    try:
        user_auth = decode_jwt(token.credentials)
    except jwt.exceptions.DecodeError:
        print(f"Decode error for token: {token}")
        raise HTTPException(status_code=400, detail="")
    except jwt.exceptions.ExpiredSignatureError:
        raise HTTPException(status_code=406, detail="Expired token")

    if not user_auth.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")

    current_time = datetime.now(UTC)
    if current_time > user_auth.exp:
        raise HTTPException(status_code=406, detail="Expired token")

    return user_auth

@router.put("/exercise/{exercise_id}", response_model=ExerciseReadSerializer)
async def update_exercise(
    exercise_id: uuid.UUID,
    data: ExerciseUpdateSerializer,
    user: Annotated[UserAuth, Depends(get_current_user)],
    db: AsyncSession = Depends(get_async_db),
) -> Exercise | None:
    """
    Lorem ipsum dolor sit amet, consetetur sadipscing elitr,
    sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam
            
    Args:
        exercise_id (uuid.UUID): Lorem ipsum dolor sit amet. 
        data (ExerciseUpdateSerializer): nonumy eirmod tempor invidun. 
        user (UserAuth): 
        db (AsyncSession): 
    Returns:
        Exercise | None: 
    Raises:
        HTTPException: If not obj
        HTTPException: If not user.is_superuser
    """
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Forbidden")

    obj = await crud.update_exercise(db, exercise_id, data)
    if not obj:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return obj


@router.get("/training_plans", response_model=list[TrainingPlanResponseSerializer])
async def get_training_plans(
    user: Annotated[UserAuth, Depends(get_current_user)],
    db: AsyncSession = Depends(get_async_db),
) -> Sequence[TrainingPlan]:
    """
    Args:
        user (UserAuth): 
        db (AsyncSession): 
    Returns:
        Sequence[TrainingPlan]: 
    Raises:
        HTTPException: If not user.is_superuser
    """
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Forbidden")

    objs = await crud.get_training_plans(
        db,
    )
    return objs


@router.get("/training_plan/{training_plan_id}", response_model=TrainingPlanReadSerializer)
async def get_training_plan(
    training_plan_id: uuid.UUID,
    user: Annotated[UserAuth, Depends(get_current_user)],
    db: AsyncSession = Depends(get_async_db),
) -> TrainingPlan | None:
    """
    Args:
        training_plan_id (uuid.UUID): 
        user (UserAuth): 
        db (AsyncSession): 
    Returns:
        TrainingPlan | None: 
    Raises:
        HTTPException: If not obj
        HTTPException: If not user.is_superuser
    """
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Forbidden")

    obj = await crud.get_training_plan(db, training_plan_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Training plan not found")
    return obj


@router.put("/training_plan/{training_plan_id}", response_model=TrainingPlanReadSerializer)
async def update_training_plan(
    training_plan_id: uuid.UUID,
    data: TrainingPlanUpdateSerializer,
    user: Annotated[UserAuth, Depends(get_current_user)],
    db: AsyncSession = Depends(get_async_db),
) -> TrainingPlan | None:
    """
    Lorem ipsum dolor sit amet, consetetur sadipscing elitr,
    sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam
        
    Args:
        training_plan_id (uuid.UUID): Lorem ipsum dolor sit amet. 
        data (TrainingPlanUpdateSerializer): 
        user (UserAuth): 
        db (AsyncSession): 
    Returns:
        TrainingPlan | None: 
    Raises:
        HTTPException: If not obj
        HTTPException: If not user.is_superuser
    """
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Forbidden")

    obj = await crud.update_training_plan(db, training_plan_id, data)
    if not obj:
        raise HTTPException(status_code=404, detail="Training plan not found")
    return obj

