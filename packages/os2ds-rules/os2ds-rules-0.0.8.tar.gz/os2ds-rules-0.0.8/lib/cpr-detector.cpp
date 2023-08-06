#include <algorithm>
#include <array>
#include <cstddef>
#include <cctype>
#include <iterator>
#include <numeric>
#include <string_view>

#include <cpr-detector.hpp>
#include <data_structures.hpp>

using namespace OS2DSRules::DataStructures;

namespace OS2DSRules {

namespace CPRDetector {

namespace {
static constexpr auto blacklist_words = std::to_array<std::string_view>(
    {"p-nr", "p.nr", "p-nummer", "pnr", "customer no", "customer-no",
     "bilagsnummer", "order number", "ordrenummer", "fakturanummer", "faknr",
     "fak-nr", "tullstatistisk", "tullstatistik", "test report no",
     "protocol no.", "dhk:tx"});

static const auto blacklist_words_set = FrozenHashSet(blacklist_words);
}; // namespace

static bool find_blacklisted_words(const std::string &content, const std::array<std::size_t, 4> indices) noexcept {

  for (std::size_t i = 1; i < 4; ++i) {
    for (std::size_t j = 0; j < i; ++j) {
      auto begin = indices[j];
      auto end = indices[i] - begin;

      if (end > content.size())
	end = content.size() - begin - 1;

      std::string target = content.substr(begin, end);
      std::transform(target.begin(), target.end(), target.begin(),
                     [](unsigned char c) { return std::tolower(c); });

      if (blacklist_words_set.contains(target))
	return true;
    }
  }

  return false;
}

void CPRDetector::reset(CPRDetectorState &state) noexcept {
  // Set the detector state to Empty.
  state = CPRDetectorState::Empty;
}

char CPRDetector::update(char c, CPRDetectorState new_state,
                         CPRDetectorState &old_state,
                         Predicate is_acceptable) noexcept {
  if (is_acceptable(c)) {
    // If c is in the set of acceptable tokens, change state and return c.
    old_state = new_state;
    return c;
  } else {
    // Reset detector state and return 0.
    reset(old_state);
    return 0;
  }
}

bool CPRDetector::check_day_month(const std::string &cpr,
                                  CPRDetectorState &state) noexcept {
  // Convert the first four digits representing day and month to ints.
  int day = std::stoi(std::string(cpr, 0, 2));
  int month = std::stoi(std::string(cpr, 2, 2));

  if (month == 2) {
    if (day == 29)
      // It is February 29th. Raise a flag to indicate that this should be a
      // leap year.
      return true;
    else if (day > 29)
      // February 30th and 31st are invalid dates, so do a reset.
      reset(state);
  } else if (day > 30 && !((month > 7 && month % 2 == 0) ||
                           (month < 8 && month % 2 != 0))) {
    // The 31st of April, June, September or November are invalid dates.
    reset(state);
  }

  // We can't tell from the day-month combination if this should be a leap year.
  return false;
}

void CPRDetector::check_leap_year(const std::string &cpr,
                                  CPRDetectorState &state) noexcept {
  // Convert the digits representing a year to an int.
  int year = std::stoi(std::string(cpr, 4, 2));
  int control = std::stoi(std::string(cpr, 6, 1));

  // If it is not a leap year, then reset.
  if (control < 4 && year == 0)
    reset(state);

  if (year % 4 != 0)
    reset(state);
}

void CPRDetector::check_and_append_cpr(std::string &cpr, MatchResults &results,
                                       size_t begin, size_t end) noexcept {
  // Convert the 4 control digits to an int.
  int control = std::stoi(std::string(cpr, 6, 4));

  // We reject the control sequence '0000'.
  if (control > 0) {
    MatchResult result(cpr, begin, end, CPRDetector::sensitivity);

    if (check_mod11_ && !check_mod11(result))
      return;

    results.push_back(result);
  }
}

bool CPRDetector::check_mod11(const MatchResult &result) noexcept {
  // Perform the modulus 11 rule check
  std::array<int, 10> factors = {0};

  // Convert every digit to an integer and multiply by the mod11 factor.
  for (std::size_t i = 0; i < 10; ++i) {
    factors[i] =
        static_cast<int>(result.match()[i] - '0') * modulus11_factors[i];
  }

  // Take the sum of all factors.
  auto sum = std::accumulate(std::begin(factors), std::end(factors), 0);

  // Check that the sum is ok.
  return sum % 11 == 0;
}

bool CPRDetector::examine_context(const std::string &content) noexcept {
  std::size_t spaces = 3;
  std::array<std::size_t, 4> indices = {0, 0, 0, 0};

  for (std::size_t i = 0; i < content.size(); ++i) {
    if (content[i] == ' ') {
      indices[4 - spaces] = i;
      --spaces;
      if (spaces == 0) {
	if (find_blacklisted_words(content, indices))
	  return true;
	
	spaces = 3;
	indices[0] = indices[3] + 1;
      }
    }
  }

  if (find_blacklisted_words(content, indices))
    return true;

  return false;
}

MatchResults CPRDetector::find_matches(const std::string &content) noexcept {
  MatchResults results;

  if (content.size() < 10) {
    return results;
  }

  if (examine_context_ && examine_context(content)) {
    return results;
  }

  // Initialize.
  CPRDetectorState state = CPRDetectorState::Empty;
  std::string cpr(10, 0);
  char previous = 0;
  std::size_t count = 0;
  std::size_t begin = 0;
  bool allow_separator, leap_year = false;
  Predicate is_acceptable = [](char) { return false; };

  for (auto it = std::begin(content); it != std::end(content); ++it) {
    switch (state) {
    case CPRDetectorState::Empty:
      if (!is_previous_ok(previous)) {
        previous = *it;
        continue;
      }

      is_acceptable = make_predicate('0', '1', '2', '3');
      update(*it, CPRDetectorState::First, state, is_acceptable);
      previous = *it;

      if (state == CPRDetectorState::First) {
        cpr[0] = *it;
        begin = count;
      }

      break;
    case CPRDetectorState::First:
      if (previous == '0') {
        is_acceptable = is_nonzero_digit;
      } else if (previous == '1' || previous == '2') {
        is_acceptable = is_digit;
      } else if (previous == '3') {
        is_acceptable = make_predicate('0', '1');
      } else {
        reset(state);
        previous = *it;
        ++count;
        continue;
      }

      previous = cpr[1] =
          update(*it, CPRDetectorState::Second, state, is_acceptable);

      if (previous != 0)
        // Next time, we allow a space.
        allow_separator = true;

      break;
    case CPRDetectorState::Second:
      is_acceptable = make_predicate('0', '1');
      previous = cpr[2] =
          update(*it, CPRDetectorState::Third, state, is_acceptable);

      break;
    case CPRDetectorState::Third:
      if (previous == '0') {
        is_acceptable = is_nonzero_digit;
      } else if (previous == '1') {
        is_acceptable = make_predicate('0', '1', '2');
      } else {
        reset(state);
        previous = 0;
        ++count;
        continue;
      }

      previous = cpr[3] =
          update(*it, CPRDetectorState::Fourth, state, is_acceptable);

      leap_year = check_day_month(cpr, state);

      if (previous != 0)
        // Next time, we allow a space.
        allow_separator = true;

      break;
    case CPRDetectorState::Fourth:
      is_acceptable = is_digit;

      previous = cpr[4] =
          update(*it, CPRDetectorState::Fifth, state, is_acceptable);

      break;
    case CPRDetectorState::Fifth:
      if (previous == '0') {
        is_acceptable = is_nonzero_digit;
      } else {
        is_acceptable = is_digit;
      }

      previous = cpr[5] =
          update(*it, CPRDetectorState::Sixth, state, is_acceptable);

      if (previous != 0)
        // Next time we allow one of the valid separators.
        allow_separator = true;

      break;
    case CPRDetectorState::Sixth:
      if (allow_separator && is_separator(*it)) {
        // Skip one of the valid separator characters.
        allow_separator = false;
	++count;
        continue;
      }

      is_acceptable = is_digit;
      previous = cpr[6] =
          update(*it, CPRDetectorState::Seventh, state, is_acceptable);

      if (leap_year)
        check_leap_year(cpr, state);

      break;
    case CPRDetectorState::Seventh:
      is_acceptable = is_digit;
      previous = cpr[7] =
          update(*it, CPRDetectorState::Eighth, state, is_acceptable);

      break;
    case CPRDetectorState::Eighth:
      is_acceptable = is_digit;
      previous = cpr[8] =
          update(*it, CPRDetectorState::Match, state, is_acceptable);

      break;
    case CPRDetectorState::Match:
      is_acceptable = is_digit;
      cpr[9] = update(*it, CPRDetectorState::Match, state, is_acceptable);

      auto ahead = it;
      if (is_previous_ok(*(++ahead)))
        check_and_append_cpr(cpr, results, begin, count);

      previous = *it;
      allow_separator = false;
      reset(state);

      break;
    }

    ++count;
  }

  return results;
}

}; // namespace CPRDetector
}; // namespace OS2DSRules
