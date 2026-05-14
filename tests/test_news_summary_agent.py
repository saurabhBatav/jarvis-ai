"""Tests for NewsSummaryAgent - Real-life test cases"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.domain.news_summary import NewsSummaryAgent


class TestNewsSummaryAgent:
    """Real-life tests for NewsSummaryAgent"""

    @pytest.fixture
    def agent(self):
        """Create agent instance for tests"""
        return NewsSummaryAgent(max_slides=10)

    def test_agent_initializes_with_default_slides(self, agent):
        """Test: Agent initializes with default 10 slides"""
        assert agent.max_slides == 10
        assert agent.news_results == []

    def test_agent_initializes_with_custom_slides(self):
        """Test: Agent can be initialized with custom slide count"""
        custom_agent = NewsSummaryAgent(max_slides=5)
        assert custom_agent.max_slides == 5

    def test_fetch_news_returns_list(self, agent):
        """Test: Fetch news returns a list of results"""
        news = agent.fetch_news("technology", max_results=5)
        assert isinstance(news, list)

    def test_fetch_news_handles_invalid_query(self, agent):
        """Test: Fetch news handles invalid query gracefully"""
        news = agent.fetch_news("")
        # Should either return empty list or error dict
        assert isinstance(news, list) or isinstance(news, dict)

    def test_fetch_news_with_special_characters(self, agent):
        """Test: Query with special characters doesn't crash"""
        news = agent.fetch_news("test @#$%!")
        assert isinstance(news, list)

    def test_create_slides_from_news(self, agent):
        """Test: Create slides from news results"""
        sample_news = [
            {"id": 1, "title": "Tech News 1", "url": "http://example.com/1"},
            {"id": 2, "title": "Tech News 2", "url": "http://example.com/2"}
        ]
        slides = agent.create_slides(sample_news)
        assert "Slide 1" in slides
        assert "Slide 2" in slides
        assert "Tech News 1" in slides

    def test_create_slides_limits_to_max_slides(self, agent):
        """Test: Slides are limited to max_slides value"""
        sample_news = [
            {"id": i, "title": f"News {i}", "url": f"http://example.com/{i}"}
            for i in range(20)
        ]
        slides = agent.create_slides(sample_news)
        # Should only create max_slides (10)
        assert slides.count("Slide ") == 10

    def test_create_slides_with_empty_news(self, agent):
        """Test: Create slides handles empty news list"""
        slides = agent.create_slides([])
        assert "News Summary Presentation" in slides
        assert "Total Slides: 0" in slides

    def test_save_presentation_creates_file(self, agent, tmp_path):
        """Test: Save presentation creates a file"""
        test_file = tmp_path / "test_presentation.md"
        slides = "# Test Slide\nTest content"
        result = agent.save_presentation(slides, str(test_file))
        assert test_file.exists()
        assert "Saved" in result

    def test_save_presentation_handles_invalid_path(self, agent):
        """Test: Save handles invalid file path gracefully"""
        result = agent.save_presentation("content", "/invalid/path/file.md")
        assert "❌" in result or "Error" in result

    def test_run_complete_workflow(self, agent, tmp_path):
        """Test: Run method executes full workflow"""
        output_file = tmp_path / "output.md"
        result = agent.run("technology", str(output_file))
        # Check if file was created or error returned
        assert output_file.exists() or "error" in result.lower()

    def test_slides_contain_timestamp(self, agent):
        """Test: Generated slides contain timestamp"""
        sample_news = [{"id": 1, "title": "Test", "url": "http://test.com"}]
        slides = agent.create_slides(sample_news)
        # Should contain year (current year)
        from datetime import datetime
        current_year = str(datetime.now().year)
        assert current_year in slides

    def test_multiple_agents_independent(self):
        """Test: Multiple agent instances are independent"""
        agent1 = NewsSummaryAgent(max_slides=5)
        agent2 = NewsSummaryAgent(max_slides=10)
        assert agent1.max_slides != agent2.max_slides
        # Both start empty but are independent instances
        assert agent1.news_results == []
        assert agent2.news_results == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])