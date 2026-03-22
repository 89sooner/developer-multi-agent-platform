export type RequestType = "feature" | "bugfix" | "refactor" | "review" | "test_plan";
export type WriteAction = "create_pr" | "comment_pr" | "update_issue" | "apply_patch" | "update_docs";

export interface ArtifactRefs {
  issue_ids: string[];
  pr_url: string | null;
  changed_files: string[];
}

export interface RequestOptions {
  include_tests: boolean;
  language: string;
  write_actions: WriteAction[];
  approval_token: string | null;
}

export interface BaseWorkflowRequest {
  request_type?: RequestType | null;
  repo_id: string;
  branch: string;
  task_text: string;
  artifacts: ArtifactRefs;
  options: RequestOptions;
}

export interface PlanRequest extends BaseWorkflowRequest {}

export interface ReviewRequest extends BaseWorkflowRequest {
  diff_text: string | null;
}

export interface TestPlanRequest {
  repo_id: string;
  branch: string;
  implementation_plan: string[];
  impacted_areas: string[];
}

export interface FeedbackRequest {
  run_id: string;
  rating: number;
  useful: boolean;
  comment: string | null;
}
