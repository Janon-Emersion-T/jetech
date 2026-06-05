from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    chat_id: str | None = None


class CustomerCreate(BaseModel):
    name: str
    company_name: str
    email: str
    phone: str
    status: str = "lead"
    notes: str | None = None


class ProjectCreate(BaseModel):
    customer_id: int
    name: str
    stack: str | None = None
    workspace_path: str | None = None
    container_name: str | None = None
    database_name: str | None = None
    ingress_host: str | None = None
    demo_url: str | None = None
    admin_login: str | None = None
    known_issues: str | None = None


class DecisionMemoryQuery(BaseModel):
    category: str = "operations"
    question: str


class DecisionMemoryResolve(BaseModel):
    category: str = "operations"
    question: str
    answer: str
    decided_by: str = "owner"
    confidence: str = "confirmed"


class ApprovalRequestCreate(BaseModel):
    action_type: str
    action_summary: str
    risk_level: str = "medium"
    target_environment: str | None = None


class ApprovalResponseCommand(BaseModel):
    command_text: str


class ReportCreate(BaseModel):
    kind: str
    summary: str
    status: str = "queued"
    delivery_channel: str = "whatsapp_pending"


class EmergencyStopRequest(BaseModel):
    command_text: str


class ChatSessionCreate(BaseModel):
    title: str | None = None


class ChatSessionRename(BaseModel):
    title: str


class PromptTemplatesPayload(BaseModel):
    templates: dict[str, str]


class SocialChannelsPayload(BaseModel):
    channels: dict


class SystemModePayload(BaseModel):
    settings: dict
