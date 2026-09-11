# Characterize a reviewed private source snapshot without sourcing its workflow.
# This is an audit, not a production science implementation or a security sandbox.
# No downloads, installation, report generation, or evaluation of top-level code.
args <- commandArgs(trailingOnly = TRUE)
source_path <- if (length(args)) args[[1]] else "blueberry_climate_analog_workflow.R"
if (!file.exists(source_path)) stop("Private reference file is required locally; it is not bundled.")
expected_md5 <- "6310a0da64316868fb465e86d85481d4"
if (!identical(unname(tools::md5sum(source_path)), expected_md5)) {
  stop("Reference changed. Review it before updating the audit fingerprint.")
}
expressions <- parse(source_path, keep.source = TRUE)
definitions <- Filter(function(x) {
  is.call(x) && identical(x[[1]], as.name("<-")) &&
    is.call(x[[3]]) && identical(x[[3]][[1]], as.name("function"))
}, as.list(expressions))
names(definitions) <- vapply(definitions, function(x) as.character(x[[2]]), character(1))
selected <- c(
  "is_chill_hour", "saturation_vapor_pressure", "vpd_from_t_rh",
  "first_date_reaching", "median_offset_date", "chill_window_dates",
  "safe_quantile", "scale_high_risk", "max_consecutive_true",
  "safe_kernel_similarity", "safe_quantile_value", "score_lower_is_better",
  "score_higher_is_better", "score_reference_range", "score_system_chill",
  "classify_detailed_production_system", "rescale_safe"
)
stopifnot(all(selected %in% names(definitions)))
# Only these 17 reviewed function declarations are evaluated, in isolation.
reference <- new.env(parent = baseenv())
reference$cfg <- list(chill_hour_threshold_c = 7.2)
reference$median <- stats::median
for (name in selected) eval(definitions[[name]], envir = reference)
passed <- 0L
check <- function(label, condition) {
  if (!isTRUE(condition)) stop(paste("Characterization changed:", label))
  passed <<- passed + 1L
  cat("PASS", label, "\n")
}

check("full file parses; 332 expressions / 51 function definitions",
      length(expressions) == 332L && length(definitions) == 51L)
check("source chill includes freezing and excludes exact 7.2 C",
      identical(reference$is_chill_hour(c(-1, 0, 7.2, 8)), c(TRUE, TRUE, FALSE, FALSE)))
north_start <- reference$chill_window_dates(2001, "north")$start
south_start <- reference$chill_window_dates(2001, "south")$start
check("northern summary anchor is 31 days early; southern anchor matches",
      as.numeric(reference$median_offset_date(0, "north") - north_start) == -31 &&
      identical(reference$median_offset_date(0, "south"), south_start))
dates <- as.Date("2020-11-01") + 0:2
check("zero chill triggers at first available date even with zero accumulation",
      identical(reference$first_date_reaching(dates, c(0, 0, 0), 0), dates[[1]]))
check("degenerate reference returns 0.5 even for missing target",
      identical(reference$scale_high_risk(NA_real_, c(1, 1)), 0.5))
check("missing dry-spell flag is treated as a false break",
      identical(reference$max_consecutive_true(c(TRUE, NA, TRUE)), 1L))
check("VPD varies with humidity at the same temperature",
      reference$vpd_from_t_rh(20, 30) > reference$vpd_from_t_rh(20, 80))
# The planting rule is embedded in a top-level pipeline, so reproduce only
# its audited scalar expression here rather than evaluate that pipeline.
early_budbreak_offset <- 30
planting_end_offset <- pmax(60, early_budbreak_offset - 45)
check("planting lower clamp can put establishment end after budbreak",
      planting_end_offset > early_budbreak_offset)

# Inspect the syntax tree without evaluating any workflow pipelines or I/O.
calls <- list()
walk_calls <- function(node) {
  if (!(is.call(node) || is.expression(node) || is.pairlist(node))) return(invisible(NULL))
  if (is.call(node)) calls[[length(calls) + 1L]] <<- node
  for (i in seq_along(node)) {
    if (!identical(node[[i]], quote(expr = ))) walk_calls(node[[i]])
  }
  invisible(NULL)
}
walk_calls(expressions)
has_call <- function(wanted) any(vapply(calls, identical, logical(1), y = wanted))
assignment_names <- vapply(Filter(function(x) {
  is.symbol(x[[1]]) && as.character(x[[1]]) %in% c("<-", "=", "<<-") &&
    is.symbol(x[[2]])
}, calls), function(x) as.character(x[[2]]), character(1))
top_assignment_index <- function(name) which(vapply(as.list(expressions), function(x) {
  is.call(x) && identical(x[[1]], as.name("<-")) && identical(x[[2]], as.name(name))
}, logical(1)))

check("kernel similarity is unchanged when all query distances grow 100-fold",
      isTRUE(all.equal(reference$safe_kernel_similarity(c(1, 2, 3)),
                       reference$safe_kernel_similarity(c(100, 200, 300)))))
check("both directional reference selectors take row one, not the whole column",
      has_call(quote(reference_suitability[1, feature_name])) &&
      has_call(quote(system_matched_reference[1, feature_name])))
sample_reference <- data.frame(exposure = c(10, 20, 30, 40))
first_value <- as.numeric(sample_reference[1, "exposure", drop = FALSE])
last_value <- as.numeric(sample_reference[4, "exposure", drop = FALSE])
full_score <- reference$score_lower_is_better(30, sample_reference$exposure)
check("first-row selection makes lower-better score binary and row-order sensitive",
      reference$score_lower_is_better(30, first_value) == 0 &&
      reference$score_lower_is_better(30, last_value) == 1 &&
      full_score > 0 && full_score < 1)
check("one-value reference range accepts equality only",
      reference$score_reference_range(20, 20) == 1 &&
      reference$score_reference_range(20.1, 20) == 0)
check("one-value higher-better score collapses to a threshold",
      reference$score_higher_is_better(19.9, 20) == 0 &&
      reference$score_higher_is_better(20, 20) == 1)
classification_lookup_index <- which(vapply(as.list(expressions), function(x) {
  is.call(x) && identical(x[[1]], as.name("if")) &&
    identical(x[[2]], quote(exists("system_assignment", inherits = TRUE)))
}, logical(1)))
check("analogue session lookup and scores precede system_assignment construction",
      length(classification_lookup_index) == 1L &&
      classification_lookup_index < top_assignment_index("system_assignment") &&
      top_assignment_index("analog_results") < top_assignment_index("system_assignment"))
check("genotype metadata uses target_system with no active assignment anywhere",
      !"target_system" %in% assignment_names &&
      has_call(quote(system_distance(preferred_production_system, target_system))))
check("master answer chooses positional system row 32, not a target key",
      has_call(quote(production_system_result$production_system[32])))
incomplete_year_schema <- any(vapply(calls, function(x) {
  identical(x[[1]], as.name("tibble")) &&
    identical(names(x)[-1], c("point_id", "site", "hemisphere", "crop_year", "chill_start", "chill_end"))
}, logical(1)))
mock_years <- dplyr::bind_rows(
  data.frame(point_id = "synthetic", point_type = "Target", crop_year = 2020),
  data.frame(point_id = "synthetic", crop_year = 2021)
)
check("incomplete-year return omits point_type and splits a location's summary groups",
      incomplete_year_schema &&
      dplyr::n_groups(dplyr::group_by(mock_years, point_id, point_type)) == 2L)

# Additional scalar consequences of reviewed, embedded expressions. These
# examples characterize language/rule behavior, not real field observations.
check("all-missing rain and freeze observations can become zero exposure",
      sum(c(NA_real_, NA_real_), na.rm = TRUE) == 0 &&
      as.numeric(any(c(NA_real_, NA_real_) <= -2.2, na.rm = TRUE)) == 0)
check("missing total risk falls into Very high catch-all",
      identical(dplyr::case_when(
        NA_real_ < 25 ~ "Low", NA_real_ < 50 ~ "Moderate",
        NA_real_ < 75 ~ "High", TRUE ~ "Very high"
      ), "Very high"))
check("auto-classifying chill gives full chill-alignment score across 0 to 800 hours",
      all(vapply(c(0, 50, 99, 100, 299, 300, 800), function(x) {
        reference$score_system_chill(x, reference$classify_detailed_production_system(x))
      }, numeric(1)) == 1))
check("unknown genotype input receives neutral rescale score",
      identical(reference$rescale_safe(c(1, 2, NA_real_)), c(0, 100, 50)))
base_scores <- c(40, 75, 60)
check("common positive environment-support multiplier cannot change genotype order",
      identical(order(base_scores), order(base_scores * (0.75 + 0.25 * 20 / 100))))
cat(passed, "characterization checks passed. Known quirks are reproduced, not fixed or endorsed.\n")
