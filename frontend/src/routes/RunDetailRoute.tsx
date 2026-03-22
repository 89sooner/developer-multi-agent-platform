import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import { useNavigate } from "react-router-dom";

import { getRun } from "../api/workflows";
import type { RunDetailResponse } from "../api/contracts/responses";
import { ApiErrorBanner } from "../components/state/ApiErrorBanner";
import { EmptyState } from "../components/state/EmptyState";
import { LoadingState } from "../components/state/LoadingState";
import { WarningsBanner } from "../components/state/WarningsBanner";
import { type ClientError } from "../api/errors";
import { useSession } from "../session/SessionProvider";
import { adaptPlanRunDetail, adaptReviewRunDetail, adaptTestPlanRunDetail, isPlanLikeRunDetail, isReviewLikeRunDetail, isTestPlanLikeRunDetail } from "../components/workflows/runDetailAdapter";
import { RunOverviewCard } from "../components/workflows/RunOverviewCard";
import { PlanResultPanel } from "../components/workflows/PlanResultPanel";
import { EvidenceList } from "../components/workflows/EvidenceList";
import { MetadataPanel } from "../components/workflows/MetadataPanel";
import { RawJsonDrawer } from "../components/workflows/RawJsonDrawer";
import { ReviewResultPanel } from "../components/workflows/ReviewResultPanel";
import { TestPlanResultPanel } from "../components/workflows/TestPlanResultPanel";

function toClientError(error: unknown): ClientError | null {
  if (error && typeof error === "object" && "clientError" in error) {
    return (error as { clientError: ClientError }).clientError;
  }
  return null;
}

export function RunDetailRoute() {
  const navigate = useNavigate();
  const { runId = "" } = useParams();
  const { bearerToken, language, setLastRunId } = useSession();
  const [data, setData] = useState<RunDetailResponse | null>(null);
  const [error, setError] = useState<ClientError | null>(null);

  const requestContext = useMemo(
    () => ({ bearerToken, language, requestId: `fe_run_${runId}` }),
    [bearerToken, language, runId]
  );

  useEffect(() => {
    let active = true;
    getRun(runId, requestContext)
      .then((response) => {
        if (!active) {
          return;
        }
        setData(response);
        setLastRunId(response.run_id);
        setError(null);
      })
      .catch((candidate: unknown) => {
        if (!active) {
          return;
        }
        setError(toClientError(candidate));
      });
    return () => {
      active = false;
    };
  }, [runId, requestContext, setLastRunId]);

  if (error) {
    return <ApiErrorBanner error={error} />;
  }
  if (!data) {
    return <LoadingState title={`Loading run ${runId}`} />;
  }

  const adaptedPlan = isPlanLikeRunDetail(data) ? adaptPlanRunDetail(data) : null;
  const adaptedReview = isReviewLikeRunDetail(data) ? adaptReviewRunDetail(data) : null;
  const adaptedTestPlan = isTestPlanLikeRunDetail(data) ? adaptTestPlanRunDetail(data) : null;
  const warnings = adaptedPlan?.warnings ?? adaptedReview?.warnings ?? adaptedTestPlan?.warnings ?? [];
  const confidence = adaptedPlan?.confidence ?? adaptedReview?.confidence ?? adaptedTestPlan?.confidence;

  return (
    <div className="route-stack">
      {warnings.length > 0 && confidence === "low" ? <WarningsBanner warnings={warnings} title="Result completed with limited backend context" /> : null}
      <RunOverviewCard
        primaryIntent={data.primary_intent}
        secondaryIntents={data.secondary_intents}
        selectedAgents={data.selected_agents}
        status={data.status}
        confidence={confidence}
      />
      {adaptedPlan ? (
        <>
          <PlanResultPanel
            summary={adaptedPlan.summary}
            impactedAreas={adaptedPlan.impactedAreas}
            implementationPlan={adaptedPlan.implementationPlan}
            tests={adaptedPlan.tests}
            risks={adaptedPlan.risks}
            openQuestions={adaptedPlan.openQuestions}
            onCreateTestPlan={() =>
              navigate("/workflows/new?mode=test-plan", {
                state: {
                  repoId: (data.request.repo_id as string) ?? "",
                  branch: (data.request.branch as string) ?? "main",
                  implementationPlan: adaptedPlan.implementationPlan,
                  impactedAreas: adaptedPlan.impactedAreas
                }
              })
            }
          />
          <EvidenceList evidence={adaptedPlan.evidence} />
        </>
      ) : adaptedReview ? (
        <>
          <ReviewResultPanel
            summary={adaptedReview.summary}
            readinessVerdict={adaptedReview.readinessVerdict}
            findings={adaptedReview.findings}
            missingTests={adaptedReview.missingTests}
            risks={adaptedReview.risks}
          />
          <EvidenceList evidence={adaptedReview.evidence} />
        </>
      ) : adaptedTestPlan ? (
        <TestPlanResultPanel
          unitTests={adaptedTestPlan.unitTests}
          integrationTests={adaptedTestPlan.integrationTests}
          regressionTargets={adaptedTestPlan.regressionTargets}
          edgeCases={adaptedTestPlan.edgeCases}
          executionOrder={adaptedTestPlan.executionOrder}
        />
      ) : (
        <EmptyState title="No recognized workflow result available" body="This run detail route currently renders semantic sections only when the nested result matches the supported plan, review, or test-plan contracts." />
      )}
      <MetadataPanel
        runId={data.run_id}
        traceId={data.trace_id}
        modelVersion={data.model_version}
        skillVersions={data.skill_versions}
        promptVersions={data.prompt_versions}
        userId={data.user_id}
        repoScope={data.repo_scope}
      />
      <RawJsonDrawer requestPayload={data.request} resultPayload={data.result} />
    </div>
  );
}
