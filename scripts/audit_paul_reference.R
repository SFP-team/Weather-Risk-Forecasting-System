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
  "safe_quantile", "scale_high_risk", "max_consecutive_true"
)
stopifnot(all(selected %in% names(definitions)))
# Only the nine reviewed function declarations are evaluated, in isolation.
reference <- new.env(parent = baseenv())
reference$cfg <- list(chill_hour_threshold_c = 7.2)
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
cat(passed, "characterization checks passed. Known quirks are reproduced, not fixed or endorsed.\n")
