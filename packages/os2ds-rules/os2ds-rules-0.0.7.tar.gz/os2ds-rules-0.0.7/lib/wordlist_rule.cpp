#include <cstddef>
#include <os2dsrules.hpp>
#include <string_view>

#include <wordlist_rule.hpp>

namespace OS2DSRules {

namespace WordListRule {

void WordListRule::check_match(MatchResults &results,
                               const std::string candidate,
                               const std::size_t start,
                               const std::size_t stop) const noexcept {
  if (contains(candidate)) {
    results.push_back(MatchResult(candidate, start, stop));
  }
}

[[nodiscard]] MatchResults
WordListRule::find_matches(const std::string &content) const noexcept {
  MatchResults results;

  static const auto is_delimiter =
      make_predicate(' ', '\n', '.', ',', '\t', '!', '?');

  std::size_t start = 0;
  for (std::size_t i = 0; i < content.size(); ++i) {
    if (is_delimiter(content[i])) {
      check_match(results, content.substr(start, i - start), start, i);
      start = i + 1;
    }
  }

  check_match(results, content.substr(start), start, content.size() - 1);

  return results;
}

[[nodiscard]] bool
WordListRule::contains(const std::string_view target) const noexcept {
  return words_.contains(target);
}

[[nodiscard]] bool
WordListRule::contains(const std::string target) const noexcept {
  return contains(std::string_view(target.cbegin(), target.cend()));
}

[[nodiscard]] bool
WordListRule::contains(const std::string::const_iterator start,
                       const std::string::const_iterator stop) const noexcept {
  return contains(std::string_view(start, stop));
}

}; // namespace WordListRule

}; // namespace OS2DSRules
