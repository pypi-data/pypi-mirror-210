#include <algorithm>
#include <array>
#include <string_view>

#include <os2dsrules.hpp>
#include <data_structures.hpp>
#include <name_rule.hpp>

using namespace OS2DSRules::DataStructures;

namespace OS2DSRules {

namespace NameRule {
using namespace std::string_view_literals;

namespace {
static constexpr auto firstnames = std::to_array({
#include "datasets/female_firstnames.txt"
#include "datasets/male_firstnames.txt"
});

static constexpr auto lastnames = std::to_array<std::string_view>({
#include "datasets/lastnames.txt"
});
static const auto firstnames_set = FrozenHashSet(firstnames);
static const auto lastnames_set = FrozenHashSet(lastnames);
}; // namespace

MatchResult compose(const MatchResult &mr1, const MatchResult &mr2) noexcept {
  std::string match_string = mr1.match() + " " + mr2.match();
  return MatchResult(match_string, mr1.start(), mr2.end());
}

[[nodiscard]] MatchResults
NameRule::find_matches(const std::string &content) const noexcept {
  MatchResults results;

  static constexpr auto is_end_of_word = make_predicate(' ', '.', '\n', '?', '-', '\t','\0');

  bool in_word = false;
  auto word_begin = content.cbegin();

  for (auto iter = content.cbegin(); iter != content.cend(); ++iter) {
    if (!in_word && std::isupper(*iter)) {
      word_begin = iter;
      in_word = true;
    }

    if (in_word && is_end_of_word(*iter)) {
      auto word_end = iter;

      if (contains(word_begin, word_end)) {
        MatchResult result(
            std::string(word_begin, word_end),
            static_cast<std::size_t>(
                std::distance(content.cbegin(), word_begin)),
            static_cast<std::size_t>(std::distance(content.begin(), word_end)));

        results.push_back(result);
      }

      in_word = false;
    }
  }

  if (in_word) {
    auto word_end = content.cend();

    if (contains(word_begin, word_end)) {
      MatchResult result(
          std::string(word_begin, word_end),
          static_cast<std::size_t>(std::distance(content.cbegin(), word_begin)),
          static_cast<std::size_t>(std::distance(content.begin(), word_end) - 1));

      results.push_back(result);
    }
  }

  return filter_matches(results);
}

[[nodiscard]] bool
NameRule::contains(const std::string_view target) const noexcept {
  std::string target_upper(target);
  std::transform(target.begin(), target.end(), target_upper.begin(),
                 [](auto ch) { return std::toupper(ch); });

  return firstnames_set.contains(target_upper.c_str()) ||
         lastnames_set.contains(target_upper.c_str());
}

[[nodiscard]] bool NameRule::contains(const std::string target) const noexcept {
  return contains(std::string_view(target.cbegin(), target.cend()));
}

[[nodiscard]] bool
NameRule::contains(const std::string::const_iterator start,
                   const std::string::const_iterator stop) const noexcept {
  return contains(std::string_view(start, stop));
}

[[nodiscard]] MatchResults
NameRule::filter_matches(const MatchResults &matches) const noexcept {
  MatchResults results;

  std::optional<MatchResult> cursor = std::nullopt;

  for (auto m : matches) {
    if (cursor) {
      if (m.is_after(cursor.value())) {
        cursor = std::make_optional(compose(cursor.value(), m));
      } else {
        results.push_back(cursor.value());
        cursor = std::make_optional(m);
      }
    } else {
      cursor = std::make_optional(m);
    }
  }

  if (cursor) {
    results.push_back(cursor.value());
  }

  return results;
}

}; // namespace NameRule

}; // namespace OS2DSRules
