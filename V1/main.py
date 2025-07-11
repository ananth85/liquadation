#!/usr/bin/env python3
"""
Liquidation Document Generation Agent - Main CLI Interface
Multi-Agent Control Plane (MCP) for synthetic liquidation document generation
"""

import asyncio
import click
import logging
import os
import json
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from agents.supervisor_agent import SupervisorAgent

# Setup logging
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
log_file = os.getenv('LOG_FILE', 'liquidation_agent.log')

logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Global supervisor instance
supervisor: Optional[SupervisorAgent] = None

async def initialize_supervisor():
    """Initialize the supervisor agent with configuration from environment variables"""
    global supervisor
    
    # Load configuration from environment variables
    config = {
        # LLM Provider Configuration
        'llm_api_key': os.getenv('LLM_API_KEY'),
        'llm_base_url': os.getenv('LLM_BASE_URL'),
        'llm_model': os.getenv('LLM_MODEL', 'gpt-3.5-turbo'),
        'llm_max_tokens': int(os.getenv('LLM_MAX_TOKENS', '4000')),
        'llm_temperature': float(os.getenv('LLM_TEMPERATURE', '0.7')),
        'llm_timeout': int(os.getenv('LLM_TIMEOUT', '30')),
        
        # Legacy OpenAI (fallback)
        'openai_api_key': os.getenv('OPENAI_API_KEY'),
        
        # External APIs
        'abn_api_key': os.getenv('ABN_API_KEY'),
        
        # Directories
        'templates_folder': os.getenv('TEMPLATES_FOLDER', 'templates'),
        'output_dir': os.getenv('OUTPUT_DIR', 'output_pdfs'),
        'sample_folder': os.getenv('SAMPLE_FOLDER', 'sample'),
        
        # System settings
        'auto_analyze_new_pdfs': os.getenv('AUTO_ANALYZE_NEW_PDFS', 'true').lower() == 'true',
        'auto_generate_templates': os.getenv('AUTO_GENERATE_TEMPLATES', 'true').lower() == 'true',
        'debug_mode': os.getenv('DEBUG_MODE', 'false').lower() == 'true',
        'fallback_generation': os.getenv('FALLBACK_GENERATION', 'true').lower() == 'true'
    }
    
    supervisor = SupervisorAgent(config=config, logger=logger)
    
    # Perform health check
    health = await supervisor.health_check()
    logger.info(f"System health check: {health['supervisor']['status']}")
    
    for agent_name, agent_health in health['agents'].items():
        if agent_health['status'] != 'healthy':
            logger.warning(f"Agent {agent_name}: {agent_health['status']} - {', '.join(agent_health['issues'])}")

@click.group()
@click.option('--debug', is_flag=True, help='Enable debug logging')
def cli(debug):
    """Liquidation Document Generation Agent - AI-powered document automation"""
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)

@cli.command()
@click.argument('prompt', required=True)
@click.option('--output-dir', '-o', default='output_pdfs', help='Output directory for PDFs')
@click.option('--format', 'output_format', default='json', type=click.Choice(['json', 'summary']), help='Output format')
def prompt(prompt, output_dir, output_format):
    """Generate liquidation documents from a free-form prompt
    
    Example:
    python main.py prompt "Generate liquidation docs for a fintech startup in Sydney with debt issues"
    """
    async def run():
        await initialize_supervisor()
        
        try:
            click.echo(f"🤖 Generating liquidation documents from prompt...")
            click.echo(f"📝 Prompt: {prompt}")
            
            result = await supervisor.generate_from_prompt(prompt)
            
            if result['success']:
                company_data = result['company_data']
                documents = result['documents']
                
                click.echo(f"✅ Generated documents for: {company_data.get('company_name', 'Unknown')}")
                click.echo(f"🏢 Industry: {company_data.get('industry', 'Unknown')}")
                click.echo(f"📍 Location: {company_data.get('address', {}).get('state', 'Unknown')}")
                
                successful_docs = len([d for d in documents if d['success']])
                click.echo(f"📄 Generated {successful_docs} documents:")
                
                for doc in documents:
                    if doc['success']:
                        filename = doc['pdf_result']['filename']
                        click.echo(f"   • {doc['document_type']}: {filename}")
                
                if output_format == 'json':
                    # Save full results
                    output_file = Path(output_dir) / f"prompt_generation_{result['pipeline_id']}.json"
                    with open(output_file, 'w') as f:
                        json.dump(result, f, indent=2, default=str)
                    click.echo(f"📋 Full results saved to: {output_file}")
                
            else:
                click.echo("❌ Document generation failed", err=True)
                if 'error' in result:
                    click.echo(f"   Error: {result['error']}", err=True)
                
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            raise click.Abort()
        finally:
            if supervisor:
                await supervisor.cleanup_resources()
    
    asyncio.run(run())

@cli.command()
@click.argument('csv_path', type=click.Path(exists=True))
@click.option('--output-dir', '-o', default='output_pdfs', help='Output directory for PDFs')
def csv(csv_path, output_dir):
    """Generate liquidation documents from CSV data file
    
    Example:
    python main.py csv companies.csv
    """
    async def run():
        await initialize_supervisor()
        
        try:
            click.echo(f"📊 Processing CSV file: {csv_path}")
            
            result = await supervisor.generate_from_csv(csv_path)
            
            if result['success']:
                batch_results = result['batch_results']
                successful = result['successful']
                failed = result['failed']
                
                click.echo(f"✅ Batch processing completed:")
                click.echo(f"   📄 Successful: {successful}")
                click.echo(f"   ❌ Failed: {failed}")
                click.echo(f"   📊 Total: {result['total']}")
                
                # Show details for successful generations
                for batch_result in batch_results:
                    if batch_result['success']:
                        company_name = batch_result['company_data']['company_name']
                        doc_count = len([d for d in batch_result['documents'] if d['success']])
                        click.echo(f"   • {company_name}: {doc_count} documents")
                
                # Save results
                output_file = Path(output_dir) / f"csv_generation_{result['pipeline_id']}.json"
                with open(output_file, 'w') as f:
                    json.dump(result, f, indent=2, default=str)
                click.echo(f"📋 Full results saved to: {output_file}")
                
            else:
                click.echo("❌ CSV processing failed", err=True)
                
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            raise click.Abort()
        finally:
            if supervisor:
                await supervisor.cleanup_resources()
    
    asyncio.run(run())

@cli.command()
@click.argument('abn', required=True)
@click.option('--output-dir', '-o', default='output_pdfs', help='Output directory for PDFs')
def abn(abn, output_dir):
    """Generate liquidation documents from ABN lookup
    
    Example:
    python main.py abn 12345678901
    """
    async def run():
        await initialize_supervisor()
        
        try:
            click.echo(f"🔍 Looking up ABN: {abn}")
            
            result = await supervisor.generate_from_abn(abn)
            
            if result['success']:
                company_data = result['company_data']
                documents = result['documents']
                
                click.echo(f"✅ Found company: {company_data.get('entity_name', 'Unknown')}")
                click.echo(f"🏢 Entity type: {company_data.get('entity_type', 'Unknown')}")
                click.echo(f"📍 Address: {company_data.get('address', {}).get('state', 'Unknown')}")
                
                successful_docs = len([d for d in documents if d['success']])
                click.echo(f"📄 Generated {successful_docs} documents:")
                
                for doc in documents:
                    if doc['success']:
                        filename = doc['pdf_result']['filename']
                        click.echo(f"   • {doc['document_type']}: {filename}")
                
                # Save results
                output_file = Path(output_dir) / f"abn_generation_{result['pipeline_id']}.json"
                with open(output_file, 'w') as f:
                    json.dump(result, f, indent=2, default=str)
                click.echo(f"📋 Full results saved to: {output_file}")
                
            else:
                click.echo("❌ ABN lookup failed", err=True)
                
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            raise click.Abort()
        finally:
            if supervisor:
                await supervisor.cleanup_resources()
    
    asyncio.run(run())

@cli.command()
@click.option('--count', '-c', default=1, help='Number of synthetic companies to generate')
@click.option('--industry', help='Specific industry for generated companies')
@click.option('--state', help='Australian state for generated companies')
@click.option('--output-dir', '-o', default='output_pdfs', help='Output directory for PDFs')
def generate(count, industry, state, output_dir):
    """Generate synthetic liquidation documents automatically
    
    Example:
    python main.py generate --count 5 --industry "Technology Services" --state NSW
    """
    async def run():
        await initialize_supervisor()
        
        try:
            click.echo(f"🎲 Generating {count} synthetic liquidation scenarios...")
            
            if industry:
                click.echo(f"🏭 Industry: {industry}")
            if state:
                click.echo(f"📍 State: {state}")
            
            successful = 0
            failed = 0
            
            for i in range(count):
                try:
                    # Generate unique prompts for variety
                    base_prompts = [
                        f"Generate documents for a {industry or 'small business'} company in {state or 'Australia'} facing financial difficulties",
                        f"Create liquidation docs for a {industry or 'professional services'} firm with operational challenges",
                        f"Generate documents for a {industry or 'retail'} business with cash flow problems",
                        f"Create liquidation scenario for a {industry or 'technology'} startup with market issues"
                    ]
                    
                    prompt = base_prompts[i % len(base_prompts)]
                    result = await supervisor.generate_from_prompt(prompt)
                    
                    if result['success']:
                        company_name = result['company_data']['company_name']
                        click.echo(f"✅ Generated: {company_name}")
                        successful += 1
                    else:
                        click.echo(f"❌ Failed generation {i+1}")
                        failed += 1
                        
                except Exception as e:
                    click.echo(f"❌ Error in generation {i+1}: {e}")
                    failed += 1
            
            click.echo(f"\n📊 Batch Results:")
            click.echo(f"   ✅ Successful: {successful}")
            click.echo(f"   ❌ Failed: {failed}")
            click.echo(f"   📄 Total: {count}")
                
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            raise click.Abort()
        finally:
            if supervisor:
                await supervisor.cleanup_resources()
    
    asyncio.run(run())

@cli.command()
def status():
    """Check system status and agent health"""
    async def run():
        await initialize_supervisor()
        
        try:
            # Get agent status
            agents_info = await supervisor.list_agents()
            health = await supervisor.health_check()
            
            click.echo("🏥 System Health Check")
            click.echo("=" * 50)
            
            # Supervisor status
            supervisor_health = health['supervisor']
            status_icon = "✅" if supervisor_health['status'] == 'healthy' else "⚠️" if supervisor_health['status'] == 'degraded' else "❌"
            click.echo(f"{status_icon} Supervisor: {supervisor_health['status']}")
            if supervisor_health['issues']:
                for issue in supervisor_health['issues']:
                    click.echo(f"   • {issue}")
            
            click.echo("\n🤖 Agent Status")
            click.echo("-" * 30)
            
            for agent_name, agent_info in agents_info['agents'].items():
                agent_health = health['agents'][agent_name]
                status_icon = "✅" if agent_health['status'] == 'healthy' else "⚠️" if agent_health['status'] == 'degraded' else "❌"
                
                status = agent_info['status']
                click.echo(f"{status_icon} {agent_name.replace('_', ' ').title()}: {agent_health['status']}")
                click.echo(f"   Capabilities: {', '.join(agent_info['capabilities'])}")
                click.echo(f"   Queue: {status['queued_tasks']} tasks, Completed: {status['completed_tasks']}")
                
                if agent_health['issues']:
                    for issue in agent_health['issues']:
                        click.echo(f"   ⚠️ {issue}")
                click.echo()
            
            # Check PDF engines
            if supervisor.pdf_generation_agent:
                engines = supervisor.pdf_generation_agent.get_available_engines()
                click.echo(f"📄 Available PDF Engines: {', '.join(engines) if engines else 'None'}")
            
            # Check LLM Provider
            if supervisor.llm_generation_agent:
                llm_client = supervisor.llm_generation_agent.client
                if llm_client:
                    base_url = supervisor.llm_generation_agent.base_url
                    if base_url:
                        click.echo(f"🧠 Custom LLM Provider: Connected ({base_url})")
                    else:
                        click.echo("🧠 OpenAI API: Connected")
                else:
                    click.echo("🧠 LLM Provider: Not configured (using fallback)")
                
        except Exception as e:
            click.echo(f"❌ Status check failed: {e}", err=True)
        finally:
            if supervisor:
                await supervisor.cleanup_resources()
    
    asyncio.run(run())

@cli.command()
@click.option('--templates-dir', default='templates', help='Templates directory')
def templates():
    """List available document templates"""
    async def run():
        await initialize_supervisor()
        
        try:
            templates_result = await supervisor.template_engine_agent.add_task("list_templates", {})
            templates_task = await supervisor.template_engine_agent.execute_next_task()
            
            if templates_task and templates_task.result:
                templates_list = templates_task.result['templates']
                
                click.echo("📄 Available Document Templates")
                click.echo("=" * 40)
                
                for template in templates_list:
                    status_icon = "✅" if template['valid'] else "❌"
                    size_kb = template['size'] / 1024
                    click.echo(f"{status_icon} {template['name']} ({size_kb:.1f} KB)")
                    
                    if not template['valid']:
                        click.echo(f"   ❌ Error: {template.get('error', 'Unknown error')}")
                
                click.echo(f"\nTotal: {len(templates_list)} templates")
            else:
                click.echo("❌ Failed to list templates")
                
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
        finally:
            if supervisor:
                await supervisor.cleanup_resources()
    
    asyncio.run(run())

@cli.command()
@click.option('--days', default=7, help='Delete files older than N days')
@click.option('--dry-run', is_flag=True, help='Show what would be deleted without deleting')
def cleanup(days, dry_run):
    """Clean up old generated PDF files"""
    async def run():
        await initialize_supervisor()
        
        try:
            if dry_run:
                click.echo(f"🧹 Dry run: Would delete PDF files older than {days} days")
                # For dry run, we'd need to implement a separate check method
                click.echo("   (Dry run not fully implemented)")
            else:
                click.echo(f"🧹 Cleaning up PDF files older than {days} days...")
                
                result = supervisor.pdf_generation_agent.cleanup_old_files(days)
                
                if result['success']:
                    click.echo(f"✅ Deleted {result['deleted_count']} files")
                    for file in result['deleted_files']:
                        click.echo(f"   • {file}")
                else:
                    click.echo(f"❌ Cleanup failed: {result['error']}")
                
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
        finally:
            if supervisor:
                await supervisor.cleanup_resources()
    
    asyncio.run(run())

@cli.command()
def setup():
    """Setup environment and check dependencies"""
    click.echo("🔧 Liquidation Document Generator Setup")
    click.echo("=" * 40)
    
    # Check Python version
    import sys
    click.echo(f"🐍 Python: {sys.version}")
    
    # Check dependencies
    dependencies = [
        ('pandas', 'CSV processing'),
        ('jinja2', 'Template rendering'),
        ('reportlab', 'PDF generation'),
        ('openai', 'LLM integration'),
        ('faker', 'Synthetic data generation'),
        ('click', 'CLI interface'),
        ('aiohttp', 'HTTP requests')
    ]
    
    click.echo("\n📦 Dependencies:")
    for package, description in dependencies:
        try:
            __import__(package)
            click.echo(f"✅ {package}: Available ({description})")
        except ImportError:
            click.echo(f"❌ {package}: Missing ({description})")
    
    # Check environment variables
    click.echo("\n🔑 Environment Variables:")
    env_vars = [
        ('LLM_API_KEY', 'Custom LLM Provider API key'),
        ('LLM_BASE_URL', 'Custom LLM Provider base URL'),
        ('OPENAI_API_KEY', 'OpenAI API access (fallback)'),
        ('ABN_API_KEY', 'ABN Lookup API access (optional)')
    ]
    
    for var, description in env_vars:
        value = os.getenv(var)
        if value:
            masked = f"{value[:8]}..." if len(value) > 8 else "***"
            click.echo(f"✅ {var}: Set ({masked}) - {description}")
        else:
            click.echo(f"⚠️ {var}: Not set - {description}")
    
    # Check directories
    click.echo("\n📁 Directories:")
    directories = [
        os.getenv('TEMPLATES_FOLDER', 'templates'),
        os.getenv('OUTPUT_DIR', 'output_pdfs'),
        os.getenv('SAMPLE_FOLDER', 'sample'),
        os.getenv('DATA_FOLDER', 'data')
    ]
    for directory in directories:
        path = Path(directory)
        if path.exists():
            click.echo(f"✅ {directory}/: Exists")
        else:
            click.echo(f"⚠️ {directory}/: Will be created")
            path.mkdir(exist_ok=True)
    
    click.echo("\n✅ Setup complete! You can now run:")
    click.echo("   python main.py prompt \"Generate docs for a tech startup with cash flow issues\"")
    click.echo("   python main.py status")

if __name__ == '__main__':
    cli() 